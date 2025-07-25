#!/usr/bin/env python3
"""
Soul Chat Robot - ADB控制器模块
用于连接、控制安卓设备以及截图
"""

import os
import subprocess
import time
import tempfile
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any, Union


class ADBController:
    """
    ADB控制器类
    负责与安卓设备通信，执行截图、点击、输入文字等操作
    """
    
    def __init__(self, adb_path: str = "adb"):
        """
        初始化ADB控制器
        
        :param adb_path: ADB可执行文件路径，默认为"adb"（假设已添加到PATH中）
        """
        self.adb_path = adb_path
        self.device_id = None
        self.screen_size = None
    
    def run_adb_command(self, command: List[str], shell: bool = False) -> Tuple[bool, str]:
        """
        执行ADB命令
        
        :param command: ADB命令列表
        :param shell: 是否使用shell=True
        :return: (成功标志, 输出结果)
        """
        try:
            if self.device_id and not shell:
                # 如果有选定设备，添加 -s 参数
                full_command = [self.adb_path, "-s", self.device_id] + command
            else:
                if shell:
                    # Shell模式下，命令应该是单个字符串
                    full_command = f"{self.adb_path} {' '.join(command)}"
                else:
                    full_command = [self.adb_path] + command
            
            # 执行命令
            if shell:
                result = subprocess.run(
                    full_command, 
                    shell=True,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                result = subprocess.run(
                    full_command, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # 检查命令是否成功
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, f"错误: {result.stderr}"
                
        except Exception as e:
            return False, f"执行ADB命令时出错: {str(e)}"
    
    def get_devices(self) -> List[Dict[str, str]]:
        """
        获取连接的设备列表
        
        :return: 设备列表，每个设备为字典 {"id": "设备ID", "status": "设备状态"}
        """
        success, output = self.run_adb_command(["devices", "-l"])
        
        if not success:
            print(f"获取设备列表失败: {output}")
            return []
        
        devices = []
        lines = output.strip().split('\n')
        
        # 跳过第一行（标题行）
        for line in lines[1:]:
            if not line.strip():
                continue
                
            parts = line.split()
            if len(parts) >= 2:
                device_id = parts[0]
                status = parts[1]
                
                # 提取额外信息
                model = "未知"
                for part in parts[2:]:
                    if part.startswith("model:"):
                        model = part.split(":", 1)[1]
                        break
                
                devices.append({
                    "id": device_id,
                    "status": status,
                    "model": model
                })
        
        return devices
    
    def connect_device(self, device_id: str) -> bool:
        """
        连接到指定的设备
        
        :param device_id: 设备ID
        :return: 是否连接成功
        """
        # 验证设备是否存在
        devices = self.get_devices()
        device_exists = any(d["id"] == device_id for d in devices)
        
        if not device_exists:
            print(f"设备 {device_id} 未连接")
            return False
        
        # 设置当前设备ID
        self.device_id = device_id
        
        # 获取屏幕尺寸
        self.update_screen_size()
        
        return True
    
    def update_screen_size(self) -> bool:
        """
        更新屏幕尺寸信息
        
        :return: 是否更新成功
        """
        if not self.device_id:
            print("未连接设备")
            return False
        
        success, output = self.run_adb_command(["shell", "wm", "size"])
        
        if not success:
            print(f"获取屏幕尺寸失败: {output}")
            return False
        
        # 解析输出 "Physical size: 1080x2340"
        try:
            size_part = output.strip().split(": ")[-1]
            width, height = map(int, size_part.split("x"))
            self.screen_size = (width, height)
            return True
        except Exception as e:
            print(f"解析屏幕尺寸失败: {str(e)}")
            self.screen_size = None
            return False
    
    def take_screenshot(self) -> Optional[bytes]:
        """
        获取屏幕截图
        
        :return: 截图的二进制数据，失败时返回None
        """
        if not self.device_id:
            print("未连接设备")
            return None
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 在设备上截图
            success1, output1 = self.run_adb_command(["shell", "screencap", "-p", "/sdcard/screenshot.png"])
            if not success1:
                print(f"截图失败: {output1}")
                os.unlink(temp_path)
                return None
            
            # 将截图从设备拉到电脑
            success2, output2 = self.run_adb_command(["pull", "/sdcard/screenshot.png", temp_path])
            if not success2:
                print(f"拉取截图失败: {output2}")
                os.unlink(temp_path)
                return None
            
            # 删除设备上的临时文件
            self.run_adb_command(["shell", "rm", "/sdcard/screenshot.png"])
            
            # 读取截图数据
            with open(temp_path, 'rb') as f:
                screenshot_data = f.read()
            
            # 删除本地临时文件
            os.unlink(temp_path)
            
            return screenshot_data
            
        except Exception as e:
            print(f"截图过程中出错: {str(e)}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None
    
    def tap(self, x: int, y: int) -> bool:
        """
        在指定坐标点击屏幕
        
        :param x: X坐标
        :param y: Y坐标
        :return: 是否点击成功
        """
        if not self.device_id:
            print("未连接设备")
            return False
        
        success, output = self.run_adb_command(["shell", "input", "tap", str(x), str(y)])
        
        if not success:
            print(f"点击屏幕失败: {output}")
            return False
        
        return True
    
    def input_text(self, text: str) -> bool:
        """
        输入文本
        
        :param text: 要输入的文本
        :return: 是否输入成功
        """
        if not self.device_id:
            print("未连接设备")
            return False
        
        # 替换特殊字符
        safe_text = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        
        success, output = self.run_adb_command(["shell", "input", "text", safe_text])
        
        if not success:
            print(f"输入文本失败: {output}")
            return False
        
        return True
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        滑动屏幕
        
        :param x1: 起始X坐标
        :param y1: 起始Y坐标
        :param x2: 结束X坐标
        :param y2: 结束Y坐标
        :param duration: 滑动持续时间（毫秒）
        :return: 是否滑动成功
        """
        if not self.device_id:
            print("未连接设备")
            return False
        
        success, output = self.run_adb_command([
            "shell", "input", "swipe", 
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
        
        if not success:
            print(f"滑动屏幕失败: {output}")
            return False
        
        return True
    
    def press_key(self, key_code: int) -> bool:
        """
        按下按键
        
        :param key_code: 按键代码
        :return: 是否按键成功
        """
        if not self.device_id:
            print("未连接设备")
            return False
        
        success, output = self.run_adb_command(["shell", "input", "keyevent", str(key_code)])
        
        if not success:
            print(f"按键失败: {output}")
            return False
        
        return True
    
    def press_back(self) -> bool:
        """
        按下返回键
        
        :return: 是否成功
        """
        return self.press_key(4)  # 4是返回键的keycode
    
    def press_home(self) -> bool:
        """
        按下Home键
        
        :return: 是否成功
        """
        return self.press_key(3)  # 3是Home键的keycode
