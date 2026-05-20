"""
工字形截面类
"""

from typing import Tuple, Dict
import numpy as np
from .base import Section


class IBeamSection(Section):
    """
    工字形截面（I型钢）

    参数:
        h: 总高度 (m)
        b: 翼缘宽度 (m)
        tw: 腹板厚度 (m)
        tf: 翼缘厚度 (m)
    """

    def __init__(self, h: float, b: float, tw: float, tf: float, name: str = None):
        """
        初始化工字形截面

        Args:
            h: 总高度 (m)
            b: 翼缘宽度 (m)
            tw: 腹板厚度 (m)
            tf: 翼缘厚度 (m)
            name: 截面名称（可选）
        """
        if h <= 0 or b <= 0 or tw <= 0 or tf <= 0:
            raise ValueError("所有截面尺寸必须为正值")
        if h < 2 * tf:
            raise ValueError("总高度必须大于两倍翼缘厚度")

        self.h = h  # 总高度
        self.b = b  # 翼缘宽度
        self.tw = tw  # 腹板厚度
        self.tf = tf  # 翼缘厚度
        self.hw = h - 2 * tf  # 腹板净高

        super().__init__(name or "工字形截面")

    def get_area(self) -> float:
        """
        计算截面面积

        Returns:
            截面面积 A = 2 × b × tf + tw × (h - 2×tf) (m^2)
        """
        area_flanges = 2 * self.b * self.tf
        area_web = self.tw * self.hw
        return area_flanges + area_web

    def get_moment_of_inertia(self, axis: str = 'z') -> float:
        """
        计算惯性矩

        Args:
            axis: 'z' 强轴（绕腹板方向弯曲）
                  'y' 弱轴（绕翼缘方向弯曲）

        Returns:
            惯性矩 (m^4)
        """
        if axis == 'z':
            # 强轴惯性矩
            # 上翼缘
            I_flange1 = self.b * self.tf ** 3 / 12
            I_flange1 += self.b * self.tf * ((self.h - self.tf) / 2) ** 2

            # 下翼缘（相同）
            I_flange2 = I_flange1

            # 腹板
            I_web = self.tw * self.hw ** 3 / 12

            return I_flange1 + I_flange2 + I_web
        else:
            # 弱轴惯性矩
            # 翼缘
            I_flanges = 2 * (self.tf * self.b ** 3 / 12)

            # 腹板
            I_web = self.hw * self.tw ** 3 / 12

            return I_flanges + I_web

    def get_section_modulus(self, axis: str = 'z') -> float:
        """
        计算截面模量

        Args:
            axis: 轴向

        Returns:
            截面模量 W = I / y_max (m^3)
        """
        I = self.get_moment_of_inertia(axis)
        if axis == 'z':
            y_max = self.h / 2
        else:
            y_max = self.b / 2
        return I / y_max

    def get_dimensions(self) -> Dict[str, float]:
        """
        获取截面尺寸参数

        Returns:
            包含所有尺寸参数的字典
        """
        return {
            'h': self.h,
            'b': self.b,
            'tw': self.tw,
            'tf': self.tf
        }

    def get_extreme_fiber_distances(self) -> Tuple[float, float]:
        """
        获取截面边缘到中性轴的距离

        对于对称工字形截面，上下边缘距离相等

        Returns:
            (上边缘距离, 下边缘距离) (m)
        """
        half_height = self.h / 2
        return (half_height, half_height)

    def get_web_area(self) -> float:
        """
        计算腹板面积

        Returns:
            腹板面积 (m^2)
        """
        return self.tw * self.hw

    def get_flange_area(self) -> float:
        """
        计算单个翼缘面积

        Returns:
            单个翼缘面积 (m^2)
        """
        return self.b * self.tf

    def get_shear_area(self, axis: str = 'z') -> float:
        """
        计算剪切面积

        对于工字形截面，剪力主要由腹板承担

        Args:
            axis: 轴向

        Returns:
            有效剪切面积 (m^2)
        """
        if axis == 'z':
            # 强轴弯曲时，剪力主要由腹板承担
            return self.hw * self.tw
        else:
            # 弱轴弯曲时
            return 2 * self.tf * self.b