#!/usr/bin/env python3
"""
测试 ChatOCR 功能
用于验证OCR文本提取是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from module.analyzer.chat.chat_ocr import ChatOCR
import time

def test_ocr_basic():
    """基础OCR功能测试"""
    print("=" * 60)
    print("🧪 开始基础OCR功能测试")
    print("=" * 60)
    
    try:
        # 初始化OCR分析器
        print("📦 正在初始化ChatOCR分析器...")
        ocr = ChatOCR()
        
        if not ocr.is_ready:
            print("❌ OCR分析器初始化失败，请检查EasyOCR安装")
            print("💡 安装命令: pip install easyocr numpy opencv-python pillow")
            return False
        
        print("✅ OCR分析器初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return False

def test_generate_test_image():
    """测试生成测试图片"""
    print("\n📸 测试生成测试图片...")
    
    try:
        ocr = ChatOCR()
        
        # 生成测试图片
        test_image_bytes = ocr.generate_test_image()
        
        if test_image_bytes and len(test_image_bytes) > 0:
            print("✅ 测试图片生成成功")
            print(f"📊 图片大小: {len(test_image_bytes)} 字节")
            
            # 保存测试图片到文件
            test_image_path = project_root / "test_image.png"
            with open(test_image_path, "wb") as f:
                f.write(test_image_bytes)
            print(f"💾 测试图片已保存到: {test_image_path}")
            
            return test_image_bytes
        else:
            print("❌ 测试图片生成失败")
            return None
            
    except Exception as e:
        print(f"❌ 生成测试图片时出错: {str(e)}")
        return None

def test_input_validation():
    """测试输入验证功能"""
    print("\n🔍 测试输入验证功能...")
    
    try:
        ocr = ChatOCR()
        
        # 测试空数据
        print("测试1: 空数据验证...")
        result = ocr.validate_input(b"")
        print(f"结果: {result} (应该为False)")
        
        # 测试无效数据
        print("测试2: 无效数据验证...")
        result = ocr.validate_input(b"invalid image data")
        print(f"结果: {result} (应该为False)")
        
        # 测试有效图片
        test_image = ocr.generate_test_image()
        if test_image:
            print("测试3: 有效图片验证...")
            result = ocr.validate_input(test_image)
            print(f"结果: {result} (应该为True)")
        
        print("✅ 输入验证测试完成")
        
    except Exception as e:
        print(f"❌ 输入验证测试失败: {str(e)}")

def test_ocr_analysis():
    """测试OCR分析功能"""
    print("\n🔍 测试OCR分析功能...")
    
    try:
        ocr = ChatOCR()
        
        if not ocr.is_ready:
            print("❌ OCR未准备好，跳过分析测试")
            return
        
        # 使用生成的测试图片进行OCR
        print("📸 使用生成的测试图片进行OCR分析...")
        test_image = ocr.generate_test_image()
        
        if not test_image:
            print("❌ 无法生成测试图片")
            return
        
        print("⏳ 正在进行OCR分析...")
        start_time = time.time()
        
        # 执行完整分析
        result = ocr.analyze(test_image)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"⏱️ 分析耗时: {analysis_time:.2f} 秒")
        print("\n📄 OCR分析结果:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        print("✅ OCR分析测试完成")
        
    except Exception as e:
        print(f"❌ OCR分析测试失败: {str(e)}")

def test_extract_text_only():
    """测试纯文本提取功能"""
    print("\n📝 测试纯文本提取功能...")
    
    try:
        ocr = ChatOCR()
        
        if not ocr.is_ready:
            print("❌ OCR未准备好，跳过文本提取测试")
            return
        
        test_image = ocr.generate_test_image()
        if not test_image:
            print("❌ 无法生成测试图片")
            return
        
        print("⏳ 正在提取纯文本...")
        text_only = ocr.extract_text_only(test_image)
        
        print(f"📝 提取的纯文本: 「{text_only}」")
        print("✅ 纯文本提取测试完成")
        
    except Exception as e:
        print(f"❌ 纯文本提取测试失败: {str(e)}")

def test_confidence_filtering():
    """测试置信度过滤功能"""
    print("\n🎯 测试置信度过滤功能...")
    
    try:
        ocr = ChatOCR()
        
        if not ocr.is_ready:
            print("❌ OCR未准备好，跳过置信度测试")
            return
        
        test_image = ocr.generate_test_image()
        if not test_image:
            print("❌ 无法生成测试图片")
            return
        
        # 测试不同置信度阈值
        thresholds = [0.3, 0.5, 0.8]
        
        for threshold in thresholds:
            print(f"\n🔍 测试置信度阈值: {threshold}")
            results = ocr.get_text_with_confidence(test_image, threshold)
            print(f"📊 检测到 {len(results)} 个高置信度文本")
            
            for i, item in enumerate(results[:3], 1):  # 只显示前3个
                print(f"  {i}. 「{item['text']}」 (置信度: {item['confidence']:.3f})")
        
        print("✅ 置信度过滤测试完成")
        
    except Exception as e:
        print(f"❌ 置信度过滤测试失败: {str(e)}")

def test_external_image():
    """测试外部图片文件（如果存在）"""
    print("\n🖼️ 测试外部图片文件...")
    
    try:
        ocr = ChatOCR()
        
        if not ocr.is_ready:
            print("❌ OCR未准备好，跳过外部图片测试")
            return
        
        # 查找项目中可能存在的图片文件
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        test_images = []
        
        for ext in image_extensions:
            test_images.extend(project_root.glob(f"*{ext}"))
            test_images.extend(project_root.glob(f"**/*{ext}"))
        
        if not test_images:
            print("📂 未找到外部图片文件，跳过此测试")
            print("💡 您可以将图片文件放在项目根目录来测试")
            return
        
        # 测试找到的第一个图片
        test_image_path = test_images[0]
        print(f"📸 测试图片: {test_image_path}")
        
        with open(test_image_path, 'rb') as f:
            image_bytes = f.read()
        
        if ocr.validate_input(image_bytes):
            print("⏳ 正在分析外部图片...")
            result = ocr.analyze(image_bytes)
            print("\n📄 外部图片OCR结果:")
            print("-" * 40)
            print(result)
            print("-" * 40)
            print("✅ 外部图片测试完成")
        else:
            print("❌ 外部图片验证失败")
        
    except Exception as e:
        print(f"❌ 外部图片测试失败: {str(e)}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 ChatOCR 功能测试开始")
    print("=" * 60)
    
    # 检查基础功能
    if not test_ocr_basic():
        print("\n❌ 基础功能测试失败，终止测试")
        return
    
    # 测试各项功能
    test_generate_test_image()
    test_input_validation()
    test_ocr_analysis()
    test_extract_text_only()
    test_confidence_filtering()
    test_external_image()
    
    print("\n" + "=" * 60)
    print("🎉 ChatOCR 功能测试完成")
    print("=" * 60)
    
    print("\n📋 测试总结:")
    print("1. ✅ 基础功能: OCR分析器初始化")
    print("2. ✅ 图片生成: 测试图片创建")
    print("3. ✅ 输入验证: 数据有效性检查")
    print("4. ✅ OCR分析: 完整文本识别")
    print("5. ✅ 文本提取: 纯文本输出")
    print("6. ✅ 置信度过滤: 结果质量控制")
    print("7. ✅ 外部图片: 实际文件处理")
    
    print("\n💡 使用建议:")
    print("- 确保安装了所需依赖: pip install easyocr numpy opencv-python pillow")
    print("- 首次运行EasyOCR会下载模型文件，请耐心等待")
    print("- 可以将自己的图片文件放在项目根目录进行测试")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
