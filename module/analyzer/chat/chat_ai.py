'''
@file: module/analyzer/chat/chat_ai.py
对输入图片进行分析
使用 ai
'''

import base64
import requests
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from module.analyzer.analyzer_api import Analyzer

class ChatAI(Analyzer):
    """
    ChatAI 分析器
    继承自 Analyzer
    使用AI API对图片进行分析
    """

    def __init__(self):
        """
        初始化 ChatAI 分析器
        - 写入 Prompt
        - 连接服务器（可选）
        - 测试是否正常进行（生成图片测试）
        """
        super().__init__()
        self.prompt = "请详细分析这张图片的内容，包括：1.图片中的主要物体和场景 2.颜色和构图特点 3.可能的用途或含义 4.整体视觉效果评价"
        
        # AI API配置 - 使用OpenAI GPT-4 Vision API
        self.api_key = "your-openai-api-key"  # 需要替换为实际的API密钥
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4-vision-preview"
        
        # 备用API配置 - 可以使用其他图像分析API
        self.backup_apis = {
            "azure": {
                "url": "https://your-region.api.cognitive.microsoft.com/vision/v3.2/analyze",
                "key": "your-azure-key"
            },
            "google": {
                "url": "https://vision.googleapis.com/v1/images:annotate",
                "key": "your-google-key"
            }
        }
    
    def analyze(self, image_bytes: bytes) -> str:
        """
        分析图片内容
        
        Args:
            image_bytes: 图片的字节数据
            
        Returns:
            str: 分析结果文本
        """
        try:
            # 将图片转换为base64编码
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # 首先尝试使用OpenAI API
            result = self._analyze_with_openai(base64_image)
            if result:
                return result
            
            # 如果OpenAI失败，尝试使用Azure Computer Vision
            result = self._analyze_with_azure(image_bytes)
            if result:
                return result
            
            # 如果都失败，返回基础分析
            return self._basic_image_analysis(image_bytes)
            
        except Exception as e:
            return f"图片分析失败: {str(e)}"
    
    def _analyze_with_openai(self, base64_image: str) -> str:
        """使用OpenAI GPT-4 Vision API分析图片"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"OpenAI API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"OpenAI API调用失败: {str(e)}")
            return None
    
    def _analyze_with_azure(self, image_bytes: bytes) -> str:
        """使用Azure Computer Vision API分析图片"""
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.backup_apis["azure"]["key"],
                'Content-Type': 'application/octet-stream'
            }
            
            params = {
                'visualFeatures': 'Categories,Description,Objects,Tags,Color'
            }
            
            response = requests.post(
                self.backup_apis["azure"]["url"],
                headers=headers,
                params=params,
                data=image_bytes,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._format_azure_result(result)
            else:
                print(f"Azure API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Azure API调用失败: {str(e)}")
            return None
    
    def _format_azure_result(self, result: dict) -> str:
        """格式化Azure API返回的结果"""
        analysis = []
        
        # 描述
        if 'description' in result and 'captions' in result['description']:
            captions = result['description']['captions']
            if captions:
                analysis.append(f"图片描述: {captions[0]['text']}")
        
        # 标签
        if 'tags' in result:
            tags = [tag['name'] for tag in result['tags'][:5]]
            analysis.append(f"识别标签: {', '.join(tags)}")
        
        # 物体检测
        if 'objects' in result:
            objects = [obj['object'] for obj in result['objects'][:3]]
            if objects:
                analysis.append(f"检测到的物体: {', '.join(objects)}")
        
        return "\n".join(analysis) if analysis else "无法分析图片内容"
    
    def _basic_image_analysis(self, image_bytes: bytes) -> str:
        """基础图片分析（当API不可用时的备用方案）"""
        try:
            image = Image.open(BytesIO(image_bytes))
            width, height = image.size
            mode = image.mode
            
            analysis = [
                f"图片基本信息:",
                f"- 尺寸: {width}x{height} 像素",
                f"- 颜色模式: {mode}",
                f"- 格式: {image.format or '未知'}"
            ]
            
            # 简单的颜色分析
            if mode == 'RGB':
                # 获取主要颜色
                colors = image.getcolors(maxcolors=256*256*256)
                if colors:
                    dominant_color = max(colors, key=lambda item: item[0])
                    analysis.append(f"- 主要颜色信息已提取")
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"基础图片分析失败: {str(e)}"
    
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
        
        try:
            # 尝试打开图片
            image = Image.open(BytesIO(image_bytes))
            
            # 检查图片尺寸
            width, height = image.size
            if width < 10 or height < 10:
                return False
            
            # 检查图片大小（限制在10MB以内）
            if len(image_bytes) > 10 * 1024 * 1024:
                return False
            
            # 检查图片格式
            if image.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']:
                return False
            
            return True
            
        except Exception:
            return False
    
    def generate_test_image(self) -> bytes:
        """
        生成测试图片
        
        Returns:
            bytes: 测试图片的字节数据
        """
        try:
            # 创建一个简单的测试图片
            width, height = 400, 300
            image = Image.new('RGB', (width, height), color='lightblue')
            
            # 添加一些图形元素
            draw = ImageDraw.Draw(image)
            
            # 绘制一个圆形
            draw.ellipse([50, 50, 150, 150], fill='red', outline='darkred', width=3)
            
            # 绘制一个矩形
            draw.rectangle([200, 50, 350, 150], fill='green', outline='darkgreen', width=3)
            
            # 添加文字
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                # 如果没有找到字体，使用默认字体
                font = ImageFont.load_default()
            
            draw.text((100, 200), "Test Image", fill='black', font=font)
            draw.text((100, 230), "图片分析测试", fill='navy', font=font)
            
            # 将图片转换为字节数据
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            # 如果生成失败，创建一个最简单的图片
            image = Image.new('RGB', (100, 100), color='white')
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
