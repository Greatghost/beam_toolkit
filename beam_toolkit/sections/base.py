"""
截面基类
定义截面的基本属性和方法
"""

from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np


class Section(ABC):
    """
    截面基类

    所有截面类型必须继承此类并实现其抽象方法
    """

    def __init__(self, name: str = None):
        """
        初始化截面

        Args:
            name: 截面名称（可选）
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def get_area(self) -> float:
        """
        计算截面面积

        Returns:
            截面面积 (m^2)
        """
        pass

    @abstractmethod
    def get_moment_of_inertia(self, axis: str = 'z') -> float:
        """
        计算惯性矩

        Args:
            axis: 轴向 ('z' 表示绕z轴，即绕强轴弯曲)

        Returns:
            惯性矩 (m^4)
        """
        pass

    @abstractmethod
    def get_section_modulus(self, axis: str = 'z') -> float:
        """
        计算截面模量

        Args:
            axis: 轴向

        Returns:
            截面模量 (m^3)
        """
        pass

    @abstractmethod
    def get_dimensions(self) -> dict:
        """
        获取截面尺寸参数

        Returns:
            包含所有尺寸参数的字典
        """
        pass

    @abstractmethod
    def get_extreme_fiber_distances(self) -> Tuple[float, float]:
        """
        获取截面边缘到中性轴的距离

        Returns:
            (上边缘距离, 下边缘距离) (m)
        """
        pass

    def get_radius_of_gyration(self, axis: str = 'z') -> float:
        """
        计算回转半径

        Args:
            axis: 轴向

        Returns:
            回转半径 (m)
        """
        I = self.get_moment_of_inertia(axis)
        A = self.get_area()
        return np.sqrt(I / A)

    def __repr__(self) -> str:
        dims = self.get_dimensions()
        dim_str = ', '.join(f'{k}={v:.3f}m' for k, v in dims.items())
        return f"{self.name}({dim_str})"

    def __str__(self) -> str:
        return f"{self.name}: A={self.get_area():.6f}m^2, I={self.get_moment_of_inertia():.9f}m^4"