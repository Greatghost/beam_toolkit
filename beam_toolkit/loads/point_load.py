"""
集中力荷载类
"""

from typing import Tuple, Optional
from .base import Load


class PointLoad(Load):
    """
    集中力荷载

    参数:
        position: 作用位置 (m)
        magnitude: 荷载大小 (N)，正值表示向下，负值表示向上
        direction: 力的方向（可选）
    """

    def __init__(
        self,
        position: float,
        magnitude: float,
        direction: str = 'down',
        name: str = None
    ):
        """
        初始化集中力荷载

        Args:
            position: 作用位置（从梁左端算起）(m)
            magnitude: 荷载大小 (N)
            direction: 'down' 向下（默认）或 'up' 向上
            name: 荷载名称（可选）
        """
        if position < 0:
            raise ValueError("荷载位置必须为非负值")

        self.position = position
        self._magnitude = abs(magnitude)
        self.direction = direction
        self.name = name or "集中力"

        # 调整符号，向下为正，向上为负
        if direction == 'down':
            self.magnitude = self._magnitude
        else:
            self.magnitude = -self._magnitude

    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的荷载值

        集中力在作用点以外的位置荷载值为0

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的荷载值（集中力大小或0）
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
        获取总荷载值

        Returns:
            总荷载值 (N)
        """
        return self.magnitude

    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            'point_load'
        """
        return 'point_load'

    def get_position(self) -> float:
        """
        获取荷载作用位置

        Returns:
            作用位置 (m)
        """
        return self.position

    def get_magnitude(self) -> float:
        """
        获取荷载大小（绝对值）

        Returns:
            荷载大小 (N)
        """
        return self._magnitude

    def is_downward(self) -> bool:
        """
        判断荷载是否向下

        Returns:
            是否向下
        """
        return self.direction == 'down'

    def __repr__(self) -> str:
        direction_symbol = '↓' if self.is_downward() else '↑'
        return f"PointLoad({self.position:.2f}m, {self._magnitude:.2f}N{direction_symbol})"

    def __str__(self) -> str:
        direction_str = '向下' if self.is_downward() else '向上'
        return f"集中力 @ {self.position:.2f}m, {self._magnitude:.2f}N {direction_str}"


class AxialPointLoad(Load):
    """
    轴向集中力荷载

    参数:
        position: 作用位置 (m)
        magnitude: 荷载大小 (N)
        direction: 'tension' 拉力 或 'compression' 压力
    """

    def __init__(
        self,
        position: float,
        magnitude: float,
        direction: str = 'tension',
        name: str = None
    ):
        """
        初始化轴向集中力荷载

        Args:
            position: 作用位置 (m)
            magnitude: 荷载大小 (N)
            direction: 'tension' 拉力 或 'compression' 压力
            name: 荷载名称（可选）
        """
        if position < 0:
            raise ValueError("荷载位置必须为非负值")

        self.position = position
        self._magnitude = abs(magnitude)
        self.direction = direction
        self.name = name or "轴向集中力"

        # 拉力为正，压力为负
        if direction == 'tension':
            self.magnitude = self._magnitude
        else:
            self.magnitude = -self._magnitude

    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的荷载值

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的荷载值
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
        获取总荷载值

        Returns:
            总荷载值 (N)
        """
        return self.magnitude

    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            'axial_point_load'
        """
        return 'axial_point_load'

    def __repr__(self) -> str:
        return f"AxialPointLoad({self.position:.2f}m, {self._magnitude:.2f}N, {self.direction})"

    def __str__(self) -> str:
        return f"轴向集中力 @ {self.position:.2f}m, {self._magnitude:.2f}N ({self.direction})"