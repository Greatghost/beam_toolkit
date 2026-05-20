"""
T形截面类
"""

from typing import Tuple, Dict
import numpy as np
from .base import Section


class TBeamSection(Section):
    """
    T形截面

    参数:
        h: 总高度 (m)
        b: 翼缘宽度 (m)
        tw: 腹板厚度 (m)
        tf: 翼缘厚度 (m)
    """

    def __init__(self, h: float, b: float, tw: float, tf: float, name: str = None):
        """
        初始化T形截面

        Args:
            h: 总高度 (m)
            b: 翼缘宽度 (m)
            tw: 腹板厚度 (m)
            tf: 翼缘厚度 (m)
            name: 截面名称（可选）
        """
        if h <= 0 or b <= 0 or tw <= 0 or tf <= 0:
            raise ValueError("所有截面尺寸必须为正值")
        if h < tf:
            raise ValueError("总高度必须大于翼缘厚度")

        self.h = h  # 总高度
        self.b = b  # 翼缘宽度
        self.tw = tw  # 腹板厚度
        self.tf = tf  # 翼缘厚度
        self.hw = h - tf  # 腹板净高

        # 计算中性轴位置（从底部起）
        self._calculate_neutral_axis_position()

        super().__init__(name or "T形截面")

    def _calculate_neutral_axis_position(self):
        """
        计算中性轴位置（从底部边缘算起）
        """
        # 翼缘面积和对底部的面积矩
        A_flange = self.b * self.tf
        y_flange = self.h - self.tf / 2  # 翼缘中心到底部的距离

        # 腹板面积和对底部的面积矩
        A_web = self.tw * self.hw
        y_web = self.hw / 2  # 腹板中心到底部的距离

        # 总面积和总面积矩
        A_total = A_flange + A_web
        S_total = A_flange * y_flange + A_web * y_web

        # 中性轴位置（从底部起）
        self.y_neutral_axis = S_total / A_total
        # 从顶部起的中性轴位置
        self.y_neutral_axis_from_top = self.h - self.y_neutral_axis

    def get_area(self) -> float:
        """
        计算截面面积

        Returns:
            截面面积 A = b × tf + tw × (h - tf) (m^2)
        """
        area_flange = self.b * self.tf
        area_web = self.tw * self.hw
        return area_flange + area_web

    def get_moment_of_inertia(self, axis: str = 'z') -> float:
        """
        计算惯性矩（绕水平中性轴）

        Args:
            axis: 'z' 绕z轴弯曲

        Returns:
            惯性矩 (m^4)
        """
        if axis == 'z':
            # 翼缘对中性轴的惯性矩（移轴定理）
            y_flange_center = self.h - self.tf / 2  # 翼缘中心位置
            d_flange = y_flange_center - self.y_neutral_axis  # 翼缘中心到中性轴距离
            I_flange_own = self.b * self.tf ** 3 / 12
            I_flange = I_flange_own + self.b * self.tf * d_flange ** 2

            # 腹板对中性轴的惯性矩
            y_web_center = self.hw / 2  # 腹板中心位置
            d_web = y_web_center - self.y_neutral_axis  # 腹板中心到中性轴距离
            I_web_own = self.tw * self.hw ** 3 / 12
            I_web = I_web_own + self.tw * self.hw * d_web ** 2

            return I_flange + I_web
        else:
            # 弱轴惯性矩
            I_flange = self.tf * self.b ** 3 / 12
            I_web = self.hw * self.tw ** 3 / 12
            return I_flange + I_web

    def get_section_modulus(self, axis: str = 'z') -> float:
        """
        计算截面模量

        由于T形截面不对称，上下截面模量不同

        Args:
            axis: 轴向

        Returns:
            较小的截面模量（保守设计）(m^3)
        """
        I = self.get_moment_of_inertia(axis)
        if axis == 'z':
            # 取较大的边缘距离计算最小的截面模量
            y_max = max(self.y_neutral_axis, self.y_neutral_axis_from_top)
            return I / y_max
        else:
            return I / (self.b / 2)

    def get_section_modulus_top(self) -> float:
        """
        计算上边缘截面模量

        Returns:
            上边缘截面模量 W_top = I / y_top (m^3)
        """
        I = self.get_moment_of_inertia()
        return I / self.y_neutral_axis_from_top

    def get_section_modulus_bottom(self) -> float:
        """
        计算下边缘截面模量

        Returns:
            下边缘截面模量 W_bottom = I / y_bottom (m^3)
        """
        I = self.get_moment_of_inertia()
        return I / self.y_neutral_axis

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
            'tf': self.tf,
            'y_neutral_axis': self.y_neutral_axis
        }

    def get_extreme_fiber_distances(self) -> Tuple[float, float]:
        """
        获取截面边缘到中性轴的距离

        Returns:
            (上边缘距离, 下边缘距离) (m)
        """
        return (self.y_neutral_axis_from_top, self.y_neutral_axis)

    def get_web_area(self) -> float:
        """
        计算腹板面积

        Returns:
            腹板面积 (m^2)
        """
        return self.tw * self.hw

    def get_flange_area(self) -> float:
        """
        计算翼缘面积

        Returns:
            翼缘面积 (m^2)
        """
        return self.b * self.tf

    def get_shear_area(self, axis: str = 'z') -> float:
        """
        计算剪切面积

        Args:
            axis: 轴向

        Returns:
            有效剪切面积 (m^2)
        """
        if axis == 'z':
            return self.tw * self.hw
        else:
            return self.tf * self.b