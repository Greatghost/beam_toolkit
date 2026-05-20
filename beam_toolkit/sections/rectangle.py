"""
矩形截面类
"""

from typing import Tuple, Dict
import numpy as np
from .base import Section


class RectangleSection(Section):
    """
    矩形截面

    参数:
        width: 截面宽度 (m)
        height: 截面高度 (m)
    """

    def __init__(self, width: float, height: float, name: str = None):
        """
        初始化矩形截面

        Args:
            width: 截面宽度 (m)
            height: 截面高度 (m)
            name: 截面名称（可选）
        """
        if width <= 0 or height <= 0:
            raise ValueError("截面尺寸必须为正值")
        self.width = width
        self.height = height
        super().__init__(name or "矩形截面")

    def get_area(self) -> float:
        """
        计算截面面积

        Returns:
            截面面积 A = b × h (m²)
        """
        return self.width * self.height

    def get_moment_of_inertia(self, axis: str = 'z') -> float:
        """
        计算惯性矩

        Args:
            axis: 'z' 表示绕z轴（强轴，绕宽度方向弯曲）
                  'y' 表示绕y轴（弱轴，绕高度方向弯曲）

        Returns:
            惯性矩 (m⁴)
        """
        if axis == 'z':
            # 绕z轴弯曲，中性轴平行于宽度
            return (self.width * self.height ** 3) / 12
        else:
            # 绕y轴弯曲，中性轴平行于高度
            return (self.height * self.width ** 3) / 12

    def get_section_modulus(self, axis: str = 'z') -> float:
        """
        计算截面模量

        Args:
            axis: 轴向

        Returns:
            截面模量 W = I / (h/2) (m³)
        """
        I = self.get_moment_of_inertia(axis)
        if axis == 'z':
            y_max = self.height / 2
        else:
            y_max = self.width / 2
        return I / y_max

    def get_dimensions(self) -> Dict[str, float]:
        """
        获取截面尺寸参数

        Returns:
            包含宽度、高度的字典
        """
        return {
            'width': self.width,
            'height': self.height
        }

    def get_extreme_fiber_distances(self) -> Tuple[float, float]:
        """
        获取截面边缘到中性轴的距离

        对于矩形截面，上下边缘距离相等

        Returns:
            (上边缘距离, 下边缘距离) (m)
        """
        half_height = self.height / 2
        return (half_height, half_height)

    def get_perimeter(self) -> float:
        """
        计算截面周长

        Returns:
            周长 P = 2(b + h) (m)
        """
        return 2 * (self.width + self.height)

    def get_shear_area(self, axis: str = 'z') -> float:
        """
        计算剪切面积（用于剪应力计算）

        Args:
            axis: 轴向

        Returns:
            有效剪切面积 (m²)
        """
        if axis == 'z':
            # 对于矩形截面，剪切面积约为截面积的5/6
            return self.get_area() * 5 / 6
        else:
            return self.get_area() * 5 / 6