#!/bin/bash
"""
Soul Chat Robot 启动脚本
一键启动安卓自动化控制应用
"""

echo "==================================="
echo "   Soul Chat Robot 启动脚本"
echo "==================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否在项目目录
if [ ! -f "android_control.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "正在创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "正在安装依赖包..."
pip install -r requirements.txt

# 检查ADB是否可用
if ! command -v adb &> /dev/null; then
    echo "警告: 未找到ADB，请确保已安装Android SDK并将ADB添加到PATH"
    echo "或者在启动时使用 --adb-path 参数指定ADB路径"
fi

echo "==================================="
echo "正在启动Soul Chat Robot..."
echo "==================================="

# 启动应用
python3 android_control.py --host 0.0.0.0 --port 5000 --debug
