"""
Soul Chat Robot - Analyzer API模块
结合 Prompt 分析画面截图，并返回文本功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class Analyzer(ABC):
    """
    分析器基础抽象类
    所有具体的分析器都应该继承此类
    """
    
    def __init__(self):
        """
        初始化分析器
        - 写入 Prompt
        - 连接服务器（可选）
        - 测试是否正常进行（生成图片测试）
        """
        self.prompt = None

    
    @abstractmethod
    def analyze(self, bytes) -> str:

        pass
    
    @abstractmethod
    def validate_input(self, bytes) -> bool:
        
        pass

    @abstractmethod
    def generate_test_image(self) -> bytes:
        """
        生成测试图片
        :param content: 输入内容
        :return: 图片
        """
        pass