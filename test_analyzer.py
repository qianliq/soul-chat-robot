#!/usr/bin/env python3
"""
测试多个分析器功能
使用两个分析器(ChatOCR和ChatAI)分别对外部图片进行分析
"""

import sys
import os
from pathlib import Path
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from module.analyzer.chat.chat_ocr import ChatOCR
from module.analyzer.chat.chat_ai import ChatAI

def find_test_images():
    """查找项目中的测试图片"""
    print("🔍 正在查找测试图片...")
    
    # 支持的图片格式
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']
    test_images = []
    
    # 在项目根目录查找图片
    for ext in image_extensions:
        test_images.extend(project_root.glob(f"*{ext}"))
        test_images.extend(project_root.glob(f"*{ext.upper()}"))  # 大写扩展名
        
    # 在子目录中查找图片（限制深度为2层）
    for ext in image_extensions:
        test_images.extend(project_root.glob(f"*/*{ext}"))
        test_images.extend(project_root.glob(f"*/*{ext.upper()}"))
    
    # 去重并排序
    test_images = sorted(list(set(test_images)))
    
    print(f"📁 找到 {len(test_images)} 个图片文件:")
    for i, img_path in enumerate(test_images, 1):
        file_size = img_path.stat().st_size
        print(f"  {i}. {img_path.name} ({file_size} 字节)")
    
    return test_images

def load_image(image_path: Path) -> bytes:
    """加载图片文件"""
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 加载图片失败: {str(e)}")
        return None

def test_with_ocr_analyzer(image_bytes: bytes, image_name: str):
    """使用OCR分析器测试"""
    print(f"\n🔤 使用OCR分析器分析 {image_name}")
    print("=" * 60)
    
    try:
        # 初始化OCR分析器
        print("📦 正在初始化ChatOCR分析器...")
        ocr = ChatOCR()
        
        if not ocr.is_ready:
            print("❌ OCR分析器初始化失败")
            print("💡 请安装依赖: pip install easyocr numpy opencv-python pillow")
            return None
        
        print("✅ OCR分析器初始化成功")
        
        # 验证输入
        if not ocr.validate_input(image_bytes):
            print("❌ 图片数据验证失败")
            return None
        
        print("✅ 图片数据验证通过")
        
        # 开始分析
        print("⏳ 正在进行OCR文本识别...")
        start_time = time.time()
        
        result = ocr.analyze(image_bytes)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"⏱️ OCR分析耗时: {analysis_time:.2f} 秒")
        print("\n📄 OCR分析结果:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ OCR分析失败: {str(e)}")
        return None

def test_with_ai_analyzer(image_bytes: bytes, image_name: str):
    """使用AI分析器测试"""
    print(f"\n🤖 使用AI分析器分析 {image_name}")
    print("=" * 60)
    
    try:
        # 初始化AI分析器
        print("📦 正在初始化ChatAI分析器...")
        ai = ChatAI()
        
        print("✅ AI分析器初始化成功")
        print(f"📝 分析提示词: {ai.prompt}")
        
        # 验证输入
        if not ai.validate_input(image_bytes):
            print("❌ 图片数据验证失败")
            return None
        
        print("✅ 图片数据验证通过")
        
        # 开始分析
        print("⏳ 正在进行AI图像分析...")
        print("💡 注意: AI分析可能需要有效的API密钥才能完成")
        start_time = time.time()
        
        result = ai.analyze(image_bytes)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"⏱️ AI分析耗时: {analysis_time:.2f} 秒")
        print("\n🎨 AI分析结果:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ AI分析失败: {str(e)}")
        return None

def compare_results(ocr_result: str, ai_result: str, image_name: str):
    """比较两个分析器的结果"""
    print(f"\n📊 分析结果对比 - {image_name}")
    print("=" * 60)
    
    if ocr_result and ai_result:
        print("✅ 两个分析器都成功完成分析")
        
        # 计算结果长度
        ocr_length = len(ocr_result) if ocr_result else 0
        ai_length = len(ai_result) if ai_result else 0
        
        print(f"📏 结果长度对比:")
        print(f"  OCR结果: {ocr_length} 字符")
        print(f"  AI结果:  {ai_length} 字符")
        
        # 简单的文本相似性分析
        if ocr_result and ai_result:
            # 检查是否有共同的关键词
            ocr_words = set(ocr_result.lower().split())
            ai_words = set(ai_result.lower().split())
            common_words = ocr_words.intersection(ai_words)
            
            if len(common_words) > 0:
                print(f"🔗 发现 {len(common_words)} 个共同关键词")
                print(f"   前5个: {list(common_words)[:5]}")
        
    elif ocr_result:
        print("⚠️ 只有OCR分析器成功完成分析")
    elif ai_result:
        print("⚠️ 只有AI分析器成功完成分析")
    else:
        print("❌ 两个分析器都未能成功完成分析")
    
    print("\n💭 分析器特点:")
    print("  🔤 OCR分析器: 专注于文字识别，快速准确")
    print("  🤖 AI分析器:  全面图像理解，需要API支持")

def test_single_image(image_path: Path):
    """测试单个图片"""
    print(f"\n🖼️ 开始测试图片: {image_path.name}")
    print(f"📂 文件路径: {image_path}")
    
    # 加载图片
    image_bytes = load_image(image_path)
    if not image_bytes:
        print("❌ 图片加载失败，跳过此文件")
        return
    
    print(f"✅ 图片加载成功 ({len(image_bytes)} 字节)")
    
    # 使用OCR分析器
    ocr_result = test_with_ocr_analyzer(image_bytes, image_path.name)
    
    # 使用AI分析器
    ai_result = test_with_ai_analyzer(image_bytes, image_path.name)
    
    # 比较结果
    compare_results(ocr_result, ai_result, image_path.name)

def create_test_image_if_needed():
    """如果没有外部图片，创建一个测试图片"""
    print("📸 没有找到外部图片，正在创建测试图片...")
    
    try:
        # 使用OCR分析器生成测试图片
        ocr = ChatOCR()
        test_image_bytes = ocr.generate_test_image()
        
        if test_image_bytes:
            test_image_path = project_root / "generated_test_image.png"
            with open(test_image_path, "wb") as f:
                f.write(test_image_bytes)
            print(f"✅ 测试图片已生成: {test_image_path}")
            return test_image_path
        else:
            print("❌ 测试图片生成失败")
            return None
            
    except Exception as e:
        print(f"❌ 创建测试图片时出错: {str(e)}")
        return None

def run_analyzer_tests():
    """运行分析器测试"""
    print("🚀 多分析器功能测试开始")
    print("=" * 80)
    
    # 查找测试图片
    test_images = find_test_images()
    
    if not test_images:
        print("\n⚠️ 未找到外部图片文件")
        print("💡 建议: 将图片文件放在项目根目录或子目录中")
        
        # 尝试创建测试图片
        generated_image = create_test_image_if_needed()
        if generated_image:
            test_images = [generated_image]
        else:
            print("❌ 无法进行测试，请添加图片文件")
            return
    
    # 测试每个图片
    for i, image_path in enumerate(test_images, 1):
        print(f"\n{'='*20} 测试 {i}/{len(test_images)} {'='*20}")
        test_single_image(image_path)
        
        # 如果有多个图片，询问是否继续
        if i < len(test_images):
            try:
                user_input = input(f"\n按回车继续测试下一个图片，或输入 'q' 退出: ").strip().lower()
                if user_input == 'q':
                    print("🛑 用户选择退出测试")
                    break
            except KeyboardInterrupt:
                print("\n\n⚠️ 测试被用户中断")
                break
    
    print("\n" + "=" * 80)
    print("🎉 多分析器功能测试完成")
    print("=" * 80)
    
    print("\n📋 测试总结:")
    print("1. ✅ 图片文件检索和加载")
    print("2. ✅ OCR分析器测试 (ChatOCR)")
    print("3. ✅ AI分析器测试 (ChatAI)")
    print("4. ✅ 结果对比和分析")
    
    print("\n💡 使用建议:")
    print("- OCR分析器: 安装 easyocr, numpy, opencv-python, pillow")
    print("- AI分析器: 需要配置有效的API密钥 (OpenAI/Azure/Google)")
    print("- 支持的图片格式: PNG, JPG, JPEG, GIF, BMP, WEBP, TIFF")
    print("- 将测试图片放在项目根目录或子目录中")

if __name__ == "__main__":
    try:
        run_analyzer_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
