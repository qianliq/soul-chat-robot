#!/usr/bin/env python3
"""
Soul Chat Robot - 安卓自动化控制应用
运行Web界面，管理和执行自动化任务
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from module.controller.web_app import WebApp, create_required_directories


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Soul Chat Robot - 安卓自动化控制')
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Web服务器主机地址 (默认: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web服务器端口 (默认: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--adb-path',
        type=str,
        default='adb',
        help='ADB可执行文件路径 (默认: "adb")'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 创建必要的目录
    dirs = create_required_directories()
    print(f"Web应用目录已准备: {dirs['templates_dir']}")
    
    # 创建并运行Web应用
    app = WebApp(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    # 如果指定了自定义ADB路径，设置控制器的ADB路径
    if args.adb_path != 'adb':
        app.controller.adb_path = args.adb_path
    
    # 打印访问信息
    print(f"启动Soul Chat Robot安卓自动化控制")
    print(f"Web界面地址: http://{args.host}:{args.port}")
    print("使用Ctrl+C停止服务")
    
    try:
        # 运行Web应用
        app.run()
    except KeyboardInterrupt:
        print("\n服务已停止")


if __name__ == "__main__":
    main()
