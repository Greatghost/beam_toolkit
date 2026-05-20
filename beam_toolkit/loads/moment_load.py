"""
弯矩荷载类
"""

from typing import Tuple, Optional
from .base import Load


class MomentLoad(Load):
    """
    集中弯矩荷载

    参数:
        position: 作用位置 (m)
        magnitude: 弯矩大小 (N·m)，正值表示顺时针（通常使梁上表面受拉）
        direction: 弯矩方向（可选）
    """

    def __init__(
        self,
        position: float,
        magnitude: float,
        direction: str = 'clockwise',
        name: str = None
    ):
        """
        初始化集中弯矩荷载

        Args:
            position: 作用位置（从梁左端算起）(m)
            magnitude: 弯矩大小 (N·m)
            direction: 'clockwise' 顺时针（默认）或 'counterclockwise' 逆时针
            name: 荷载名称（可选）
        """
        if position < 0:
            raise ValueError("荷载位置必须为非负值")

        self.position = position
        self._magnitude = abs(magnitude)
        self.direction = direction
        self.name = name or "集中弯矩"

        # 顺时针为正（通常使梁上表面受拉），逆时针为负
        if direction == 'clockwise':
            self.magnitude = self._magnitude
        else:
            self.magnitude = -self._magnitude

    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的弯矩值

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的弯矩值（集中弯矩大小或0）
        """
        if abs(position - self.position) < 1e-10:
            return self.magnitude
        return 0.0

    def get_load_range(self) -> Tuple[float, float]:
        """
        获取荷载作用范围

        Returns:
            (作用位置, 作用位置) (m)
        """
        return (self.position, self.position)

    def get_total_load(self) -> float:
        """
        获取总弯矩值

        Returns:
            总弯矩值 (N·m)
        """
        return self.magnitude

    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            'moment_load'
        """
        return 'moment_load'

    def get_position(self) -> float:
        """
        获取弯矩作用位置

        Returns:
            作用位置 (m)
        """
        return self.position

    def get_magnitude(self) -> float:
        """
        获取弯矩大小（绝对值）

        Returns:
            弯矩大小 (N·m)
        """
        return self._magnitude

    def is_clockwise(self) -> bool:
        """
        判断弯矩是否顺时针

        Returns:
            是否顺时针
        """
        return self.direction == 'clockwise'

    def __repr__(self) -> str:
        direction_symbol = '↻' if self.is_clockwise() else '↺'
        return f"MomentLoad({self.position:.2f}m, {self._magnitude:.2f}N·m{direction_symbol})"

    def __str__(self) -> str:
        direction_str = '顺时针' if self.is_clockwise() else '逆时针'
        return f"集中弯矩 @ {self.position:.2f}m, {self._magnitude:.2f}N·m {direction_str}"