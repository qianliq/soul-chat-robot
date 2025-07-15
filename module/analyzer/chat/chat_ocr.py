'''
@file: module/analyzer/chat/chat_ocr.py
对输入图片进行OCR文本提取
使用 EasyOCR
'''

import easyocr
import numpy as np
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cv2
from typing import List, Dict, Any
from module.analyzer.analyzer_api import Analyzer

class ChatOCR(Analyzer):
    """
    ChatOCR 分析器
    继承自 Analyzer
    使用EasyOCR对图片进行文本识别和提取
    """

    def __init__(self):
        """
        初始化 ChatOCR 分析器
        - 写入 Prompt
        - 初始化EasyOCR读取器
        - 测试是否正常进行（生成图片测试）
        """
        super().__init__()
        self.prompt = None # OCR不需要特定的Prompt
        
        # 初始化EasyOCR读取器，支持中英文
        self.supported_languages = ['ch_sim', 'en']  # 简体中文和英文
        try:
            self.reader = easyocr.Reader(self.supported_languages, gpu=False)  # 可以设置gpu=True如果有GPU
            self.is_ready = True
        except Exception as e:
            print(f"EasyOCR初始化失败: {str(e)}")
            self.reader = None
            self.is_ready = False
    
    def analyze(self, image_bytes: bytes) -> str:
        """
        对图片进行OCR文本提取
        
        Args:
            image_bytes: 图片的字节数据
            
        Returns:
            str: OCR识别结果文本
        """
        if not self.is_ready:
            return "OCR引擎未初始化，请检查EasyOCR安装"
        
        try:
            # 将字节数据转换为PIL Image
            image = Image.open(BytesIO(image_bytes))
            
            # 转换为numpy数组供EasyOCR使用
            image_np = np.array(image)
            
            # 如果是RGBA，转换为RGB
            if image_np.shape[2] == 4:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
            
            # 使用EasyOCR进行文本识别
            results = self.reader.readtext(image_np)
            
            # 格式化结果
            return self._format_ocr_results(results, image.size)
            
        except Exception as e:
            return f"OCR文本提取失败: {str(e)}"
    
    def _format_ocr_results(self, results: List, image_size: tuple) -> str:
        """
        格式化OCR识别结果
        
        Args:
            results: EasyOCR返回的结果列表
            image_size: 图片尺寸 (width, height)
            
        Returns:
            str: 格式化后的结果文本
        """
        if not results:
            return "未在图片中检测到任何文本内容"
        
        width, height = image_size
        analysis_parts = []
        
        # 添加总体信息
        analysis_parts.append(f"OCR文本提取结果 (图片尺寸: {width}x{height})")
        analysis_parts.append(f"共检测到 {len(results)} 个文本区域")
        analysis_parts.append("-" * 50)
        
        # 提取所有文本内容
        all_texts = []
        detailed_results = []
        
        for i, (bbox, text, confidence) in enumerate(results, 1):
            # 计算文本区域的中心点
            center_x = int(sum([point[0] for point in bbox]) / 4)
            center_y = int(sum([point[1] for point in bbox]) / 4)
            
            # 计算相对位置
            relative_x = center_x / width
            relative_y = center_y / height
            
            # 确定位置描述
            pos_desc = self._get_position_description(relative_x, relative_y)
            
            # 添加到结果列表
            all_texts.append(text.strip())
            detailed_results.append({
                'index': i,
                'text': text.strip(),
                'confidence': confidence,
                'position': pos_desc,
                'coordinates': (center_x, center_y)
            })
        
        # 添加完整文本内容
        analysis_parts.append("✅ 提取的完整文本内容:")
        full_text = " ".join(all_texts)
        analysis_parts.append(f"「{full_text}」")
        analysis_parts.append("")
        
        # 添加详细的分区域结果
        analysis_parts.append("📍 详细识别结果:")
        for result in detailed_results:
            confidence_stars = "⭐" * min(5, int(result['confidence'] * 5))
            analysis_parts.append(
                f"{result['index']}. 文本: 「{result['text']}」"
            )
            analysis_parts.append(
                f"   位置: {result['position']} | "
                f"置信度: {result['confidence']:.2f} {confidence_stars}"
            )
            analysis_parts.append("")
        
        # 添加统计信息
        analysis_parts.append("📊 统计信息:")
        avg_confidence = sum(r['confidence'] for r in detailed_results) / len(detailed_results)
        high_conf_count = sum(1 for r in detailed_results if r['confidence'] > 0.8)
        
        analysis_parts.append(f"- 平均置信度: {avg_confidence:.2f}")
        analysis_parts.append(f"- 高置信度文本 (>0.8): {high_conf_count}/{len(detailed_results)}")
        analysis_parts.append(f"- 总字符数: {len(full_text)}")
        
        # 语言检测
        languages_detected = self._detect_languages(all_texts)
        analysis_parts.append(f"- 检测到的语言: {', '.join(languages_detected)}")
        
        return "\n".join(analysis_parts)
    
    def _get_position_description(self, rel_x: float, rel_y: float) -> str:
        """
        根据相对坐标获取位置描述
        
        Args:
            rel_x: 相对X坐标 (0-1)
            rel_y: 相对Y坐标 (0-1)
            
        Returns:
            str: 位置描述
        """
        # 垂直位置
        if rel_y < 0.33:
            v_pos = "上部"
        elif rel_y < 0.67:
            v_pos = "中部"
        else:
            v_pos = "下部"
        
        # 水平位置
        if rel_x < 0.33:
            h_pos = "左侧"
        elif rel_x < 0.67:
            h_pos = "中央"
        else:
            h_pos = "右侧"
        
        return f"{v_pos}{h_pos}"
    
    def _detect_languages(self, texts: List[str]) -> List[str]:
        """
        简单的语言检测
        
        Args:
            texts: 文本列表
            
        Returns:
            List[str]: 检测到的语言列表
        """
        languages = set()
        
        for text in texts:
            # 检测中文字符
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                languages.add("中文")
            
            # 检测英文字符
            if any(char.isalpha() and ord(char) < 128 for char in text):
                languages.add("英文")
            
            # 检测数字
            if any(char.isdigit() for char in text):
                languages.add("数字")
        
        return list(languages) if languages else ["未知"]
    
    def validate_input(self, image_bytes: bytes) -> bool:
        """
        验证输入的图片数据是否有效
        
        Args:
            image_bytes: 图片字节数据
            
        Returns:
            bool: 验证结果
        """
        if not image_bytes or len(image_bytes) == 0:
            return False
        
        if not self.is_ready:
            return False
        
        try:
            # 尝试打开图片
            image = Image.open(BytesIO(image_bytes))
            
            # 检查图片尺寸
            width, height = image.size
            if width < 10 or height < 10:
                return False
            
            # 检查图片大小（限制在20MB以内，OCR可能需要处理更大的图片）
            if len(image_bytes) > 20 * 1024 * 1024:
                return False
            
            # 检查图片格式
            if image.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP', 'TIFF']:
                return False
            
            return True
            
        except Exception:
            return False
    
    def generate_test_image(self) -> bytes:
        """
        生成包含文本的测试图片
        
        Returns:
            bytes: 测试图片的字节数据
        """
        try:
            # 创建一个包含文本的测试图片
            width, height = 600, 400
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # 尝试加载支持中文的字体
            font_large = self._get_font(36)
            font_medium = self._get_font(24)
            font_small = self._get_font(18)
            
            # 添加各种测试文本
            texts = [
                ("OCR Test Image", 50, 50, font_large, 'black'),
                ("这是中文测试文本", 50, 100, font_medium, 'blue'),
                ("English Text Recognition", 50, 150, font_medium, 'red'),
                ("Mixed 混合文本 123456", 50, 200, font_medium, 'green'),
                ("电话: 138-0013-8000", 50, 250, font_small, 'purple'),
                ("Email: test@example.com", 50, 280, font_small, 'orange'),
                ("地址: 北京市朝阳区", 50, 310, font_small, 'navy')
            ]
            
            for text, x, y, font, color in texts:
                draw.text((x, y), text, fill=color, font=font)
            
            # 添加一个边框
            draw.rectangle([10, 10, width-10, height-10], outline='gray', width=2)
            
            # 将图片转换为字节数据
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            # 如果生成失败，创建一个最简单的文本图片
            image = Image.new('RGB', (200, 100), color='white')
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "OCR Test", fill='black')
            draw.text((10, 40), "测试文本", fill='black')
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
    
    def _get_font(self, size: int):
        """
        获取支持中文的字体
        
        Args:
            size: 字体大小
            
        Returns:
            字体对象
        """
        # macOS 中文字体路径列表
        chinese_fonts = [
            "/System/Library/Fonts/PingFang.ttc",  # 苹方字体
            "/System/Library/Fonts/STHeiti Light.ttc",  # 华文黑体
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑体
            "/System/Library/Fonts/Arial Unicode MS.ttf",  # Arial Unicode
            "/System/Library/Fonts/Helvetica.ttc",  # Helvetica
            "/Library/Fonts/Arial.ttf",  # 系统Arial
            "/System/Library/Fonts/Menlo.ttc",  # Menlo字体
        ]
        
        # 尝试加载支持中文的字体
        for font_path in chinese_fonts:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        # 如果都失败了，使用默认字体
        try:
            return ImageFont.load_default()
        except:
            # 最后的备用方案
            return ImageFont.load_default()
    
    def extract_text_only(self, image_bytes: bytes) -> str:
        """
        只提取纯文本内容，不包含位置等详细信息
        
        Args:
            image_bytes: 图片的字节数据
            
        Returns:
            str: 提取的纯文本内容
        """
        if not self.is_ready:
            return ""
        
        try:
            image = Image.open(BytesIO(image_bytes))
            image_np = np.array(image)
            
            if image_np.shape[2] == 4:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
            
            results = self.reader.readtext(image_np)
            
            # 只返回文本内容
            texts = [result[1].strip() for result in results]
            return " ".join(texts)
            
        except Exception:
            return ""
    
    def get_text_with_confidence(self, image_bytes: bytes, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        获取带置信度的文本结果
        
        Args:
            image_bytes: 图片的字节数据
            min_confidence: 最小置信度阈值
            
        Returns:
            List[Dict]: 文本结果列表，包含text, confidence, bbox等信息
        """
        if not self.is_ready:
            return []
        
        try:
            image = Image.open(BytesIO(image_bytes))
            image_np = np.array(image)
            
            if image_np.shape[2] == 4:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
            
            results = self.reader.readtext(image_np)
            
            # 过滤低置信度结果
            filtered_results = []
            for bbox, text, confidence in results:
                if confidence >= min_confidence:
                    filtered_results.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            return filtered_results
            
        except Exception:
            return []
