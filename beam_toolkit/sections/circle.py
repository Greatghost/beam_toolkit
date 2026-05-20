"""
圆形截面类
"""

from typing import Tuple, Dict
import numpy as np
from .base import Section


class CircleSection(Section):
    """
    圆形截面

    参数:
        diameter: 直径 (m)
        或者 radius: 半径 (m)
    """

    def __init__(self, diameter: float = None, radius: float = None, name: str = None):
        """
        初始化圆形截面

        Args:
            diameter: 直径 (m)，与radius二选一
            radius: 半径 (m)，与diameter二选一
            name: 截面名称（可选）
        """
        if diameter is None and radius is None:
            raise ValueError("必须提供直径或半径")
        if diameter is not None and radius is not None:
            raise ValueError("只能提供直径或半径中的一个")

        if diameter is not None:
            if diameter <= 0:
                raise ValueError("直径必须为正值")
            self.diameter = diameter
            self.radius = diameter / 2
        else:
            if radius <= 0:
                raise ValueError("半径必须为正值")
            self.radius = radius
            self.diameter = radius * 2

        super().__init__(name or "圆形截面")

    def get_area(self) -> float:
        """
        计算截面面积

        Returns:
            截面面积 A = π × r² (m^2)
        """
        return np.pi * self.radius ** 2

    def get_moment_of_inertia(self, axis: str = 'z') -> float:
        """
        计算惯性矩

        圆形截面对任何轴的惯性矩相同

        Args:
            axis: 轴向（对圆形截面无影响）

        Returns:
            惯性矩 I = π × d⁴ / 64 (m^4)
        """
        return np.pi * self.diameter ** 4 / 64

    def get_section_modulus(self, axis: str = 'z') -> float:
        """
        计算截面模量

        Args:
            axis: 轴向（对圆形截面无影响）

        Returns:
            截面模量 W = π × d³ / 32 (m^3)
        """
        return np.pi * self.diameter ** 3 / 32

    def get_dimensions(self) -> Dict[str, float]:
        """
        获取截面尺寸参数

        Returns:
            包含直径、半径的字典
        """
        return {
            'diameter': self.diameter,
            'radius': self.radius
        }

    def get_extreme_fiber_distances(self) -> Tuple[float, float]:
        """
        获取截面边缘到中性轴的距离

        对于圆形截面，上下边缘距离相等

        Returns:
            (上边缘距离, 下边缘距离) (m)
        """
        return (self.radius, self.radius)

    def get_polar_moment_of_inertia(self) -> float:
        """
        计算极惯性矩（用于扭转分析）

        Returns:
            极惯性矩 J = π × d⁴ / 32 (m^4)
        """
        return np.pi * self.diameter ** 4 / 32

    def get_perimeter(self) -> float:
        """
        计算截面周长

        Returns:
            周长 P = π × d (m)
        """
        return np.pi * self.diameter

    def get_shear_area(self, axis: str = 'z') -> float:
        """
        计算剪切面积

        Args:
            axis: 轴向（对圆形截面无影响）

        Returns:
            有效剪切面积 (m^2)
        """
        # 对于圆形截面，剪切面积约为截面积的9/10
        return self.get_area() * 9 / 10