#!/usr/bin/env python3
"""
截图功能测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from module.controller.adb_controller import ADBController


def test_screenshot():
    """测试截图功能"""
    print("=== Soul Chat Robot 截图功能测试 ===")
    
    # 创建ADB控制器
    controller = ADBController()
    
    # 获取设备列表
    print("1. 获取设备列表...")
    devices = controller.get_devices()
    
    if not devices:
        print("❌ 未找到任何设备，请确保:")
        print("   - 安卓设备已连接到电脑")
        print("   - 已启用USB调试")
        print("   - ADB驱动已正确安装")
        return False
    
    print(f"✅ 找到 {len(devices)} 个设备:")
    for i, device in enumerate(devices):
        print(f"   {i+1}. {device['id']} - {device['model']} ({device['status']})")
    
    # 连接到第一个可用设备
    available_devices = [d for d in devices if d['status'] == 'device']
    if not available_devices:
        print("❌ 没有可用的设备（状态为'device'）")
        return False
    
    target_device = available_devices[0]
    print(f"\n2. 连接到设备: {target_device['id']}")
    
    success = controller.connect_device(target_device['id'])
    if not success:
        print("❌ 连接设备失败")
        return False
    
    print("✅ 设备连接成功")
    
    if controller.screen_size:
        print(f"   屏幕分辨率: {controller.screen_size[0]} x {controller.screen_size[1]}")
    
    # 测试截图
    print("\n3. 测试截图功能...")
    screenshot_data = controller.take_screenshot()
    
    if screenshot_data:
        print(f"✅ 截图成功！获取到 {len(screenshot_data)} 字节的图像数据")
        
        # 保存截图到文件
        screenshot_path = project_root / "test_screenshot.png"
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot_data)
        
        print(f"📱 截图已保存到: {screenshot_path}")
        
        # 验证是否为有效的PNG文件
        if screenshot_data[:8] == b'\x89PNG\r\n\x1a\n':
            print("✅ 截图文件格式验证通过（PNG格式）")
        else:
            print("⚠️  截图文件格式可能有问题")
        
        return True
    else:
        print("❌ 截图失败")
        return False


def main():
    """主函数"""
    try:
        success = test_screenshot()
        if success:
            print("\n🎉 截图功能测试通过！")
        else:
            print("\n💥 截图功能测试失败！")
            print("\n故障排除建议:")
            print("1. 确保设备已连接并开启USB调试")
            print("2. 检查ADB是否正确安装: adb version")
            print("3. 检查设备权限: adb shell screencap --help")
            print("4. 尝试手动截图: adb shell screencap -p /sdcard/test.png")
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
