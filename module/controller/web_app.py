#!/usr/bin/env python3
"""
Soul Chat Robot - Web界面模块
基于Flask的Web界面，用于管理和执行自动化任务
"""

import os
import json
import logging
import base64
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_from_directory, Response, url_for

from module.controller.adb_controller import ADBController
from module.controller.task_manager import TaskManager, Task, TaskAction, Condition


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('web_app')


class WebApp:
    """Web应用类"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        """
        初始化Web应用
        
        :param host: 主机地址
        :param port: 端口号
        :param debug: 是否开启调试模式
        """
        self.host = host
        self.port = port
        self.debug = debug
        
        # 创建Flask应用
        self.app = Flask(
            __name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates')
        )
        
        # 创建ADB控制器
        self.controller = ADBController()
        
        # 创建任务管理器
        self.task_manager = TaskManager(self.controller)
        
        # 初始化路由
        self._init_routes()
    
    def _init_routes(self):
        """初始化路由"""
        
        @self.app.route('/')
        def index():
            """首页"""
            return render_template('index.html')
        
        @self.app.route('/devices', methods=['GET'])
        def get_devices():
            """获取设备列表"""
            devices = self.controller.get_devices()
            return jsonify({
                'status': 'success',
                'devices': devices,
                'connected_device': self.controller.device_id
            })
        
        @self.app.route('/connect', methods=['POST'])
        def connect_device():
            """连接设备"""
            data = request.json
            device_id = data.get('device_id')
            
            if not device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未提供设备ID'
                })
            
            success = self.controller.connect_device(device_id)
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'成功连接到设备 {device_id}',
                    'screen_size': self.controller.screen_size
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'连接设备 {device_id} 失败'
                })
        
        @self.app.route('/screenshot', methods=['GET'])
        def take_screenshot():
            """获取屏幕截图"""
            if not self.controller.device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未连接设备'
                })
            
            screenshot_data = self.controller.take_screenshot()
            
            if screenshot_data:
                # 将截图数据编码为Base64字符串
                encoded_image = base64.b64encode(screenshot_data).decode('utf-8')
                
                return jsonify({
                    'status': 'success',
                    'image': encoded_image,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': '获取截图失败'
                })
        
        @self.app.route('/tap', methods=['POST'])
        def tap_screen():
            """点击屏幕"""
            if not self.controller.device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未连接设备'
                })
            
            data = request.json
            x = data.get('x')
            y = data.get('y')
            
            if x is None or y is None:
                return jsonify({
                    'status': 'error',
                    'message': '未提供点击坐标'
                })
            
            success = self.controller.tap(int(x), int(y))
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'点击坐标 ({x}, {y}) 成功'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'点击坐标 ({x}, {y}) 失败'
                })
        
        @self.app.route('/input', methods=['POST'])
        def input_text():
            """输入文本"""
            if not self.controller.device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未连接设备'
                })
            
            data = request.json
            text = data.get('text')
            
            if not text:
                return jsonify({
                    'status': 'error',
                    'message': '未提供输入文本'
                })
            
            success = self.controller.input_text(text)
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'输入文本成功: {text}'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'输入文本失败: {text}'
                })
        
        @self.app.route('/key', methods=['POST'])
        def press_key():
            """按下按键"""
            if not self.controller.device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未连接设备'
                })
            
            data = request.json
            key_code = data.get('key_code')
            
            if key_code is None:
                return jsonify({
                    'status': 'error',
                    'message': '未提供按键代码'
                })
            
            success = self.controller.press_key(int(key_code))
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'按键 {key_code} 成功'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'按键 {key_code} 失败'
                })
        
        @self.app.route('/swipe', methods=['POST'])
        def swipe_screen():
            """滑动屏幕"""
            if not self.controller.device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未连接设备'
                })
            
            data = request.json
            x1 = data.get('x1')
            y1 = data.get('y1')
            x2 = data.get('x2')
            y2 = data.get('y2')
            duration = data.get('duration', 300)
            
            if None in (x1, y1, x2, y2):
                return jsonify({
                    'status': 'error',
                    'message': '未提供滑动坐标'
                })
            
            success = self.controller.swipe(int(x1), int(y1), int(x2), int(y2), int(duration))
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'滑动操作成功: ({x1}, {y1}) -> ({x2}, {y2})'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'滑动操作失败: ({x1}, {y1}) -> ({x2}, {y2})'
                })
        
        @self.app.route('/tasks', methods=['GET'])
        def get_tasks():
            """获取所有任务"""
            tasks = self.task_manager.get_all_tasks()
            return jsonify({
                'status': 'success',
                'tasks': [task.to_dict() for task in tasks]
            })
        
        @self.app.route('/tasks', methods=['POST'])
        def create_task():
            """创建任务"""
            data = request.json
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': '未提供任务数据'
                })
            
            try:
                task = Task.from_dict(data)
                task_id = self.task_manager.add_task(task)
                
                return jsonify({
                    'status': 'success',
                    'message': f'成功创建任务 {task.name}',
                    'task_id': task_id
                })
            except Exception as e:
                logger.error(f"创建任务失败: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f'创建任务失败: {str(e)}'
                })
        
        @self.app.route('/tasks/<task_id>', methods=['PUT'])
        def update_task(task_id):
            """更新任务"""
            data = request.json
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': '未提供任务数据'
                })
            
            try:
                task = Task.from_dict(data)
                self.task_manager.update_task(task_id, task)
                
                return jsonify({
                    'status': 'success',
                    'message': f'成功更新任务 {task.name}'
                })
            except Exception as e:
                logger.error(f"更新任务失败: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f'更新任务失败: {str(e)}'
                })
        
        @self.app.route('/tasks/<task_id>', methods=['DELETE'])
        def delete_task(task_id):
            """删除任务"""
            try:
                self.task_manager.remove_task(task_id)
                
                return jsonify({
                    'status': 'success',
                    'message': f'成功删除任务 {task_id}'
                })
            except Exception as e:
                logger.error(f"删除任务失败: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f'删除任务失败: {str(e)}'
                })
        
        @self.app.route('/tasks/<task_id>/run', methods=['POST'])
        def run_task(task_id):
            """执行任务"""
            if not self.controller.device_id:
                return jsonify({
                    'status': 'error',
                    'message': '未连接设备'
                })
            
            try:
                # 获取任务
                task = self.task_manager.get_task(task_id)
                if not task:
                    return jsonify({
                        'status': 'error',
                        'message': f'任务不存在: {task_id}'
                    })
                
                # 开始执行任务
                execution_id = self.task_manager.run_task(task_id)
                
                return jsonify({
                    'status': 'success',
                    'message': f'开始执行任务: {task.name}',
                    'execution_id': execution_id
                })
            except Exception as e:
                logger.error(f"执行任务失败: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f'执行任务失败: {str(e)}'
                })
        
        @self.app.route('/tasks/save', methods=['POST'])
        def save_tasks():
            """保存所有任务到文件"""
            data = request.json
            file_path = data.get('file_path')
            
            if not file_path:
                # 使用默认路径
                file_path = os.path.join(os.path.dirname(__file__), 'tasks.json')
            
            try:
                self.task_manager.save_tasks(file_path)
                
                return jsonify({
                    'status': 'success',
                    'message': f'成功保存任务到文件 {file_path}',
                    'file_path': file_path
                })
            except Exception as e:
                logger.error(f"保存任务失败: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f'保存任务失败: {str(e)}'
                })
        
        @self.app.route('/tasks/load', methods=['POST'])
        def load_tasks():
            """从文件加载任务"""
            data = request.json
            file_path = data.get('file_path')
            
            if not file_path:
                # 使用默认路径
                file_path = os.path.join(os.path.dirname(__file__), 'tasks.json')
            
            try:
                self.task_manager.load_tasks(file_path)
                
                return jsonify({
                    'status': 'success',
                    'message': f'成功从文件 {file_path} 加载任务',
                    'tasks': [task.to_dict() for task in self.task_manager.get_all_tasks()]
                })
            except Exception as e:
                logger.error(f"加载任务失败: {str(e)}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'message': f'从文件 {file_path} 加载任务失败'
                })
    
    def run(self):
        """启动Web应用"""
        logger.info(f"启动Web应用, 访问地址: http://{self.host}:{self.port}")
        logger.info(f"静态文件目录: {self.app.static_folder}")
        logger.info(f"模板文件目录: {self.app.template_folder}")
        self.app.run(host=self.host, port=self.port, debug=self.debug)


# 创建必要的目录
def create_required_directories():
    """创建必要的目录结构"""
    # 获取controller模块目录
    module_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建static目录
    static_dir = os.path.join(module_dir, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # 创建static/css目录
    css_dir = os.path.join(static_dir, 'css')
    os.makedirs(css_dir, exist_ok=True)
    
    # 创建static/js目录
    js_dir = os.path.join(static_dir, 'js')
    os.makedirs(js_dir, exist_ok=True)
    
    # 创建static/img目录
    img_dir = os.path.join(static_dir, 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    # 创建templates目录
    templates_dir = os.path.join(module_dir, 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    logger.info("已创建必要的目录结构")
    
    # 返回目录信息
    return {
        'module_dir': module_dir,
        'static_dir': static_dir,
        'css_dir': css_dir,
        'js_dir': js_dir,
        'img_dir': img_dir,
        'templates_dir': templates_dir
    }
    
    # 返回目录字典
    return {
        'static_dir': static_dir,
        'css_dir': css_dir,
        'js_dir': js_dir,
        'img_dir': img_dir,
        'templates_dir': templates_dir
    }


# 如果作为主程序运行
if __name__ == "__main__":
    create_required_directories()
    app = WebApp(host="0.0.0.0", port=5000, debug=True)
    app.run()
