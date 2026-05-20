"""
荷载基类
定义荷载的基本属性和方法
"""

from abc import ABC, abstractmethod
from typing import Tuple, Callable, Optional
import numpy as np


class Load(ABC):
    """
    荷载基类

    所有荷载类型必须继承此类并实现其抽象方法
    """

    def __init__(self, name: str = None):
        """
        初始化荷载

        Args:
            name: 荷载名称（可选）
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的荷载值

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的荷载值（根据荷载类型不同含义不同）
        """
        pass

    @abstractmethod
    def get_load_range(self) -> Tuple[float, float]:
        """
        获取荷载作用范围

        Returns:
            (起始位置, 结束位置) (m)
        """
        pass

    @abstractmethod
    def get_total_load(self) -> float:
        """
        获取总荷载值

        Returns:
            总荷载值（N 或 N*m）
        """
        pass

    @abstractmethod
    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            荷载类型字符串
        """
        pass

    def is_within_range(self, position: float) -> bool:
        """
        判断指定位置是否在荷载作用范围内

        Args:
            position: 位置 (m)

        Returns:
            是否在荷载范围内
        """
        start, end = self.get_load_range()
        return start <= position <= end

    def __repr__(self) -> str:
        return f"{self.name}(type={self.get_load_type()})"

    def __str__(self) -> str:
        return f"{self.name}: {self.get_load_type()}, 总值={self.get_total_load():.2f}"