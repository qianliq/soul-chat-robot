#!/usr/bin/env python3
"""
Soul Chat Robot - 任务管理器模块
定义和执行自动化任务
"""

import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict

from module.controller.adb_controller import ADBController
from module.analyzer.chat.chat_ocr import ChatOCR
from module.analyzer.chat.chat_ai import ChatAI


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('task_manager')


@dataclass
class TaskAction:
    """任务动作基类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "base"
    name: str = "未命名动作"
    description: str = ""
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行动作"""
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskAction':
        """从字典创建实例"""
        action_type = data.get('type', 'base')
        
        # 根据动作类型创建相应的动作实例
        if action_type == 'tap':
            return TapAction(**data)
        elif action_type == 'input':
            return InputTextAction(**data)
        elif action_type == 'wait':
            return WaitAction(**data)
        elif action_type == 'key':
            return KeyAction(**data)
        elif action_type == 'swipe':
            return SwipeAction(**data)
        elif action_type == 'execute_task':
            return ExecuteTaskAction(**data)
        elif action_type == 'sleep':
            return SleepAction(**data)
        else:
            return TaskAction(**data)


@dataclass
class TapAction(TaskAction):
    """点击动作"""
    type: str = "tap"
    name: str = "点击屏幕"
    x: int = 0
    y: int = 0
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行点击操作"""
        logger.info(f"执行点击操作: ({self.x}, {self.y})")
        return controller.tap(self.x, self.y)


@dataclass
class InputTextAction(TaskAction):
    """输入文本动作"""
    type: str = "input"
    name: str = "输入文本"
    text: str = ""
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行文本输入"""
        logger.info(f"执行文本输入: {self.text}")
        return controller.input_text(self.text)


@dataclass
class WaitAction(TaskAction):
    """等待动作"""
    type: str = "wait"
    name: str = "等待"
    seconds: float = 1.0
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行等待"""
        logger.info(f"等待 {self.seconds} 秒")
        time.sleep(self.seconds)
        return True


@dataclass
class KeyAction(TaskAction):
    """按键动作"""
    type: str = "key"
    name: str = "按键"
    key_code: int = 0  # 按键代码
    key_name: str = ""  # 按键名称（仅用于显示）
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行按键操作"""
        logger.info(f"执行按键: {self.key_name} (代码: {self.key_code})")
        return controller.press_key(self.key_code)


@dataclass
class SwipeAction(TaskAction):
    """滑动动作"""
    type: str = "swipe"
    name: str = "滑动屏幕"
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    duration: int = 300  # 滑动持续时间（毫秒）
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行滑动操作"""
        logger.info(f"执行滑动: 从 ({self.x1}, {self.y1}) 到 ({self.x2}, {self.y2}), 持续 {self.duration}ms")
        return controller.swipe(self.x1, self.y1, self.x2, self.y2, self.duration)


@dataclass
class ExecuteTaskAction(TaskAction):
    """执行任务动作"""
    type: str = "execute_task"
    name: str = "执行任务"
    task_id: str = ""  # 要执行的任务ID
    task_name: str = ""  # 任务名称（仅用于显示）
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行指定任务"""
        if not self.task_id:
            logger.error("未指定要执行的任务ID")
            return False
            
        # 从上下文中获取任务管理器
        task_manager = context.get('task_manager')
        if not task_manager:
            logger.error("任务管理器不可用")
            return False
            
        # 防止循环调用 - 检查调用栈
        call_stack = context.get('call_stack', [])
        if self.task_id in call_stack:
            logger.error(f"检测到循环调用任务: {self.task_id}")
            return False
            
        logger.info(f"执行子任务: {self.task_name} (ID: {self.task_id})")
        
        # 创建新的上下文，添加调用栈
        new_context = context.copy()
        new_context['call_stack'] = call_stack + [self.task_id]
        
        # 执行任务
        task = task_manager.get_task(self.task_id)
        if not task:
            logger.error(f"任务不存在: {self.task_id}")
            return False
            
        return task.execute(controller, new_context)


@dataclass
class SleepAction(TaskAction):
    """睡眠动作（等待动作的别名，为了更清晰的命名）"""
    type: str = "sleep"
    name: str = "睡眠等待"
    seconds: float = 1.0
    
    def execute(self, controller: ADBController, context: Dict[str, Any]) -> bool:
        """执行睡眠等待"""
        logger.info(f"睡眠等待 {self.seconds} 秒")
        time.sleep(self.seconds)
        return True


@dataclass
class Condition:
    """条件类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "text"  # text, image, template
    content: str = ""  # 要检测的文本或图像特征
    analyzer: str = "ocr"  # ocr, ai, template
    confidence: float = 0.7  # 匹配置信度
    template_image: bytes = field(default=None)  # 模板图像数据
    template_name: str = ""  # 模板图像名称
    template_region: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "width": 0, "height": 0})  # 截图区域
    
    def evaluate(self, image_data: bytes, context: Dict[str, Any]) -> bool:
        """评估条件是否满足"""
        if not image_data:
            logger.error("无法获取图像数据")
            return False
        
        result = False
        
        try:
            # 根据条件类型和分析器类型使用不同的处理方式
            if self.type == "text":
                # 文本匹配模式
                if self.analyzer == "ocr":
                    ocr = ChatOCR()
                    if not ocr.is_ready:
                        logger.error("OCR分析器未准备就绪")
                        return False
                    
                    text_result = ocr.analyze(image_data)
                    logger.info(f"OCR识别结果: {text_result}")
                    
                    # 检查识别文本中是否包含目标内容
                    if self.content.lower() in text_result.lower():
                        result = True
                        logger.info(f"OCR条件满足: 找到文本 '{self.content}'")
                    else:
                        logger.info(f"OCR条件不满足: 未找到文本 '{self.content}'")
                
                elif self.analyzer == "ai":
                    ai = ChatAI()
                    ai_result = ai.analyze(image_data)
                    logger.info(f"AI分析结果: {ai_result}")
                    
                    # 对于AI分析器，我们使用更灵活的匹配方式
                    if self.content.lower() in ai_result.lower():
                        result = True
                        logger.info(f"AI条件满足: 找到内容 '{self.content}'")
                    else:
                        logger.info(f"AI条件不满足: 未找到内容 '{self.content}'")
                
                else:
                    logger.error(f"文本匹配不支持分析器类型: {self.analyzer}")
            
            elif self.type == "template" and self.template_image:
                # 图像模板匹配模式
                import cv2
                import numpy as np
                
                logger.info(f"执行模板匹配: {self.template_name}")
                
                # 将图像数据转换为OpenCV格式
                img_array = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                # 将模板图像数据转换为OpenCV格式
                template_array = np.frombuffer(self.template_image, np.uint8)
                template = cv2.imdecode(template_array, cv2.IMREAD_COLOR)
                
                if img is None or template is None:
                    logger.error("无法解码图像数据")
                    return False
                
                logger.info(f"截图尺寸: {img.shape}, 模板尺寸: {template.shape}")
                
                # 如果设置了区域，则截取相应区域进行匹配
                if all(v > 0 for v in [self.template_region.get('width', 0), self.template_region.get('height', 0)]):
                    x = self.template_region.get("x", 0)
                    y = self.template_region.get("y", 0)
                    w = self.template_region.get("width", 0)
                    h = self.template_region.get("height", 0)
                    
                    logger.info(f"使用指定区域: x={x}, y={y}, w={w}, h={h}")
                    
                    # 确保区域在图像范围内
                    img_h, img_w = img.shape[:2]
                    if x + w <= img_w and y + h <= img_h:
                        roi = img[y:y+h, x:x+w]
                        logger.info(f"ROI尺寸: {roi.shape}")
                        img = roi
                    else:
                        logger.warning("指定的区域超出图像范围，使用完整图像")
                
                # 执行模板匹配
                try:
                    match_result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(match_result)
                    
                    logger.info(f"模板匹配最大值: {max_val:.4f}, 位置: {max_loc}")
                    
                    # 检查匹配度是否达到阈值
                    if max_val >= self.confidence:
                        result = True
                        logger.info(f"模板匹配条件满足: 匹配度 {max_val:.2f} >= {self.confidence}")
                    else:
                        logger.info(f"模板匹配条件不满足: 匹配度 {max_val:.2f} < {self.confidence}")
                except cv2.error as e:
                    logger.error(f"OpenCV模板匹配错误: {str(e)}")
                    return False
            
            else:
                logger.error(f"不支持的条件类型: {self.type}")
        
        except Exception as e:
            logger.error(f"条件评估时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "analyzer": self.analyzer,
            "confidence": self.confidence,
            "template_name": self.template_name,
            "template_region": self.template_region
        }
        
        # 对于模板图像，我们需要特殊处理，转换为base64字符串
        if self.template_image:
            import base64
            result["template_image"] = base64.b64encode(self.template_image).decode('utf-8')
        else:
            result["template_image"] = None
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        """从字典创建实例"""
        # 复制数据以避免修改原始数据
        condition_data = data.copy()
        
        # 处理模板图像数据
        if condition_data.get("template_image"):
            import base64
            try:
                template_image = base64.b64decode(condition_data["template_image"])
                condition_data["template_image"] = template_image
            except Exception as e:
                logger.error(f"解码模板图像数据时出错: {str(e)}")
                condition_data["template_image"] = None
        else:
            condition_data["template_image"] = None
            
        return Condition(**condition_data)


@dataclass
class Task:
    """任务类，表示一个可执行的任务流程"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "未命名任务"
    description: str = ""
    conditions: List[Condition] = field(default_factory=list)
    actions: List[TaskAction] = field(default_factory=list)
    children: List['Task'] = field(default_factory=list)
    # 任务类型: simple=简单任务, conditional=条件任务, loop=循环任务
    task_type: str = "simple"
    # 循环次数（对于循环任务）
    loop_count: int = 0
    # 是否启用
    enabled: bool = True
    
    def execute(self, controller: ADBController, context: Dict[str, Any] = None) -> bool:
        """执行任务"""
        if not self.enabled:
            logger.info(f"任务 '{self.name}' 已禁用，跳过执行")
            return False
        
        if context is None:
            context = {}
        
        success = True
        logger.info(f"开始执行任务: {self.name}")
        
        # 根据任务类型执行不同的逻辑
        if self.task_type == "simple":
            # 简单任务：直接执行所有动作
            for action in self.actions:
                if not action.execute(controller, context):
                    logger.warning(f"动作 '{action.name}' 执行失败")
                    success = False
            
        elif self.task_type == "conditional":
            # 条件任务：先获取截图，然后评估条件
            image_data = controller.take_screenshot()
            
            if not image_data:
                logger.error("无法获取截图，条件任务无法继续")
                return False
            
            # 保存截图到上下文，以便后续使用
            context['last_screenshot'] = image_data
            
            # 评估所有条件
            conditions_met = True
            for condition in self.conditions:
                if not condition.evaluate(image_data, context):
                    conditions_met = False
                    break
            
            # 如果条件满足，执行动作和子任务
            if conditions_met:
                logger.info(f"条件满足，执行任务 '{self.name}' 的动作")
                
                # 执行动作
                for action in self.actions:
                    if not action.execute(controller, context):
                        logger.warning(f"动作 '{action.name}' 执行失败")
                        success = False
                
                # 执行子任务
                for child_task in self.children:
                    if not child_task.execute(controller, context):
                        logger.warning(f"子任务 '{child_task.name}' 执行失败")
                        success = False
            else:
                logger.info(f"条件不满足，跳过任务 '{self.name}'")
                success = False
            
        elif self.task_type == "loop":
            # 循环任务：重复执行指定次数
            loop_times = max(1, self.loop_count)
            logger.info(f"循环任务 '{self.name}' 将执行 {loop_times} 次")
            
            for i in range(loop_times):
                logger.info(f"循环 {i+1}/{loop_times}")
                
                # 执行动作
                for action in self.actions:
                    if not action.execute(controller, context):
                        logger.warning(f"动作 '{action.name}' 执行失败")
                        success = False
                
                # 执行子任务
                for child_task in self.children:
                    if not child_task.execute(controller, context):
                        logger.warning(f"子任务 '{child_task.name}' 执行失败")
                        success = False
        
        else:
            logger.error(f"未知的任务类型: {self.task_type}")
            success = False
        
        logger.info(f"任务 '{self.name}' 执行{'成功' if success else '失败'}")
        return success
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conditions": [c.to_dict() for c in self.conditions],
            "actions": [a.to_dict() for a in self.actions],
            "children": [t.to_dict() for t in self.children],
            "task_type": self.task_type,
            "loop_count": self.loop_count,
            "enabled": self.enabled
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建实例"""
        # 创建基本任务对象，但不包括嵌套对象
        task_data = {
            "id": data.get("id", str(uuid.uuid4())),
            "name": data.get("name", "未命名任务"),
            "description": data.get("description", ""),
            "task_type": data.get("task_type", "simple"),
            "loop_count": data.get("loop_count", 0),
            "enabled": data.get("enabled", True),
            # 临时设置为空列表，后面再填充
            "conditions": [],
            "actions": [],
            "children": []
        }
        
        # 创建任务对象
        task = Task(**task_data)
        
        # 填充条件列表
        for condition_data in data.get("conditions", []):
            task.conditions.append(Condition.from_dict(condition_data))
        
        # 填充动作列表
        for action_data in data.get("actions", []):
            task.actions.append(TaskAction.from_dict(action_data))
        
        # 填充子任务列表
        for child_data in data.get("children", []):
            task.children.append(Task.from_dict(child_data))
        
        return task


class TaskManager:
    """任务管理器，管理所有任务"""
    
    def __init__(self, controller: ADBController):
        """
        初始化任务管理器
        
        :param controller: ADB控制器实例
        """
        self.controller = controller
        self.tasks: List[Task] = []
        self.task_file_path = None
    
    def add_task(self, task: Task) -> bool:
        """
        添加任务
        
        :param task: 任务实例
        :return: 是否添加成功
        """
        self.tasks.append(task)
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        删除任务
        
        :param task_id: 任务ID
        :return: 是否删除成功
        """
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        
        # 还需要递归检查所有子任务
        def remove_from_children(task_list: List[Task]) -> None:
            for task in task_list:
                task.children = [child for child in task.children if child.id != task_id]
                remove_from_children(task.children)
        
        remove_from_children(self.tasks)
        
        return len(self.tasks) < original_count
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        :param task_id: 任务ID
        :return: 任务实例，未找到时返回None
        """
        # 在顶层任务中查找
        for task in self.tasks:
            if task.id == task_id:
                return task
        
        # 递归查找子任务
        def find_in_children(task_list: List[Task]) -> Optional[Task]:
            for task in task_list:
                if task.id == task_id:
                    return task
                
                result = find_in_children(task.children)
                if result:
                    return result
            
            return None
        
        return find_in_children(self.tasks)
    
    def execute_task(self, task_id: str) -> bool:
        """
        执行指定任务
        
        :param task_id: 任务ID
        :return: 是否执行成功
        """
        task = self.get_task(task_id)
        
        if not task:
            logger.error(f"未找到任务 ID: {task_id}")
            return False
        
        if not self.controller.device_id:
            logger.error("未连接设备，无法执行任务")
            return False
        
        # 创建新的上下文
        context = {
            "start_time": time.time(),
            "task_id": task_id,
            "task_manager": self,  # 添加任务管理器到上下文
            "call_stack": []  # 初始化调用栈，防止循环调用
        }
        
        return task.execute(self.controller, context)
    
    def save_tasks(self, file_path: str) -> bool:
        """
        保存任务到文件
        
        :param file_path: 文件路径
        :return: 是否保存成功
        """
        try:
            task_data = [task.to_dict() for task in self.tasks]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            self.task_file_path = file_path
            logger.info(f"任务保存到文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存任务失败: {str(e)}")
            return False
    
    def load_tasks(self, file_path: str) -> bool:
        """
        从文件加载任务
        
        :param file_path: 文件路径
        :return: 是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # 清空当前任务
            self.tasks.clear()
            
            # 加载任务
            for data in task_data:
                self.tasks.append(Task.from_dict(data))
            
            self.task_file_path = file_path
            logger.info(f"从文件加载任务: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
            return False
    
    def get_all_tasks(self) -> List[Task]:
        """
        获取所有顶层任务
        
        :return: 任务列表
        """
        return self.tasks
    
    def clear_all_tasks(self) -> bool:
        """
        清空所有任务
        
        :return: 是否清空成功
        """
        self.tasks.clear()
        return True
