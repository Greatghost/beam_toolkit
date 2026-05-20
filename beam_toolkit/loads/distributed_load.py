"""
分布力荷载类
"""

from typing import Tuple, Callable, Optional
from abc import ABC
import numpy as np
from .base import Load


class DistributedLoad(Load):
    """
    分布力荷载基类

    用于表示沿梁长度分布的荷载
    """

    def __init__(
        self,
        start_position: float,
        end_position: float,
        name: str = None
    ):
        """
        初始化分布力荷载

        Args:
            start_position: 荷载起始位置 (m)
            end_position: 荷载结束位置 (m)
            name: 荷载名称（可选）
        """
        if start_position < 0 or end_position < 0:
            raise ValueError("荷载位置必须为非负值")
        if start_position > end_position:
            raise ValueError("起始位置必须小于结束位置")

        self.start_position = start_position
        self.end_position = end_position
        self.length = end_position - start_position

        super().__init__(name or "分布力")

    def get_load_range(self) -> Tuple[float, float]:
        """
        获取荷载作用范围

        Returns:
            (起始位置, 结束位置) (m)
        """
        return (self.start_position, self.end_position)

    def get_length(self) -> float:
        """
        获取荷载作用长度

        Returns:
            荷载作用长度 (m)
        """
        return self.length


class UniformDistributedLoad(DistributedLoad):
    """
    均布荷载

    参数:
        start_position: 荷载起始位置 (m)
        end_position: 荷载结束位置 (m)
        magnitude: 荷载集度 (N/m)，正值向下，负值向上
        direction: 力的方向（可选）
    """

    def __init__(
        self,
        start_position: float,
        end_position: float,
        magnitude: float,
        direction: str = 'down',
        name: str = None
    ):
        """
        初始化均布荷载

        Args:
            start_position: 荷载起始位置 (m)
            end_position: 荷载结束位置 (m)
            magnitude: 荷载集度 (N/m)
            direction: 'down' 向下（默认）或 'up' 向上
            name: 荷载名称（可选）
        """
        super().__init__(start_position, end_position, name or "均布荷载")

        self._magnitude = abs(magnitude)
        self.direction = direction

        # 向下为正，向上为负
        if direction == 'down':
            self.magnitude = self._magnitude
        else:
            self.magnitude = -self._magnitude

    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的荷载集度

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的荷载集度 (N/m)
        """
        if self.is_within_range(position):
            return self.magnitude
        return 0.0

    def get_total_load(self) -> float:
        """
        获取总荷载值

        Returns:
            总荷载值 q × L (N)
        """
        return self.magnitude * self.length

    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            'uniform_distributed_load'
        """
        return 'uniform_distributed_load'

    def get_magnitude(self) -> float:
        """
        获取荷载集度（绝对值）

        Returns:
            荷载集度 (N/m)
        """
        return self._magnitude

    def is_downward(self) -> bool:
        """
        判断荷载是否向下

        Returns:
            是否向下
        """
        return self.direction == 'down'

    def get_equivalent_point_load_position(self) -> float:
        """
        获取等效集中力作用位置（荷载中心）

        Returns:
            等效集中力位置 (m)
        """
        return self.start_position + self.length / 2

    def get_equivalent_point_load(self) -> 'PointLoad':
        """
        获取等效集中力

        Returns:
            等效集中力荷载对象
        """
        from .point_load import PointLoad
        return PointLoad(
            position=self.get_equivalent_point_load_position(),
            magnitude=self.get_total_load(),
            direction=self.direction,
            name=f"{self.name}等效集中力"
        )

    def __repr__(self) -> str:
        direction_symbol = '↓' if self.is_downward() else '↑'
        return f"UniformDistributedLoad({self.start_position:.2f}-{self.end_position:.2f}m, {self._magnitude:.2f}N/m{direction_symbol})"

    def __str__(self) -> str:
        direction_str = '向下' if self.is_downward() else '向上'
        return f"均布荷载 [{self.start_position:.2f}-{self.end_position:.2f}m], {self._magnitude:.2f}N/m {direction_str}"


class LinearDistributedLoad(DistributedLoad):
    """
    线性分布荷载（梯形荷载）

    参数:
        start_position: 荷载起始位置 (m)
        end_position: 荷载结束位置 (m)
        start_magnitude: 起始位置荷载集度 (N/m)
        end_magnitude: 结束位置荷载集度 (N/m)
    """

    def __init__(
        self,
        start_position: float,
        end_position: float,
        start_magnitude: float,
        end_magnitude: float,
        name: str = None
    ):
        """
        初始化线性分布荷载

        Args:
            start_position: 荷载起始位置 (m)
            end_position: 荷载结束位置 (m)
            start_magnitude: 起始位置荷载集度 (N/m)
            end_magnitude: 结束位置荷载集度 (N/m)
            name: 荷载名称（可选）
        """
        super().__init__(start_position, end_position, name or "线性分布荷载")

        self.start_magnitude = start_magnitude
        self.end_magnitude = end_magnitude

    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的荷载集度

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的荷载集度 (N/m)
        """
        if not self.is_within_range(position):
            return 0.0

        # 线性插值
        ratio = (position - self.start_position) / self.length
        return self.start_magnitude + ratio * (self.end_magnitude - self.start_magnitude)

    def get_total_load(self) -> float:
        """
        获取总荷载值

        Returns:
            总荷载值（梯形面积）(N)
        """
        return (self.start_magnitude + self.end_magnitude) * self.length / 2

    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            'linear_distributed_load'
        """
        return 'linear_distributed_load'

    def get_equivalent_point_load_position(self) -> float:
        """
        获取等效集中力作用位置

        对于梯形荷载，等效集中力位置按面积重心计算

        Returns:
            等效集中力位置 (m)
        """
        # 梯形重心位置公式
        if abs(self.start_magnitude - self.end_magnitude) < 1e-10:
            # 实际上是均布荷载
            return self.start_position + self.length / 2

        h1 = abs(self.start_magnitude)
        h2 = abs(self.end_magnitude)

        # 梯形重心到起点距离
        x = self.length * (h1 + 2 * h2) / (3 * (h1 + h2))

        return self.start_position + x

    def get_equivalent_point_load(self) -> 'PointLoad':
        """
        获取等效集中力

        Returns:
            等效集中力荷载对象
        """
        from .point_load import PointLoad
        return PointLoad(
            position=self.get_equivalent_point_load_position(),
            magnitude=self.get_total_load(),
            direction='down' if self.get_total_load() > 0 else 'up',
            name=f"{self.name}等效集中力"
        )

    def __repr__(self) -> str:
        return f"LinearDistributedLoad({self.start_position:.2f}-{self.end_position:.2f}m, {self.start_magnitude:.2f}-{self.end_magnitude:.2f}N/m)"

    def __str__(self) -> str:
        return f"线性分布荷载 [{self.start_position:.2f}-{self.end_position:.2f}m], {self.start_magnitude:.2f}-{self.end_magnitude:.2f}N/m"


class GeneralDistributedLoad(DistributedLoad):
    """
    任意分布荷载

    参数:
        start_position: 荷载起始位置 (m)
        end_position: 荷载结束位置 (m)
        load_function: 荷载函数 f(x) (N/m)
    """

    def __init__(
        self,
        start_position: float,
        end_position: float,
        load_function: Callable[[float], float],
        name: str = None
    ):
        """
        初始化任意分布荷载

        Args:
            start_position: 荷载起始位置 (m)
            end_position: 荷载结束位置 (m)
            load_function: 荷载函数 f(x)，返回位置x处的荷载集度 (N/m)
            name: 荷载名称（可选）
        """
        super().__init__(start_position, end_position, name or "任意分布荷载")
        self.load_function = load_function

    def get_load_value_at(self, position: float) -> float:
        """
        获取指定位置的荷载集度

        Args:
            position: 沿梁长度方向的位置 (m)

        Returns:
            该位置的荷载集度 (N/m)
        """
        if self.is_within_range(position):
            return self.load_function(position)
        return 0.0

    def get_total_load(self) -> float:
        """
        获取总荷载值

        Returns:
            总荷载值（积分）(N)
        """
        # 使用数值积分
        n_points = 100
        positions = np.linspace(self.start_position, self.end_position, n_points)
        load_values = [self.load_function(x) for x in positions]
        return np.trapz(load_values, positions)

    def get_load_type(self) -> str:
        """
        获取荷载类型

        Returns:
            'general_distributed_load'
        """
        return 'general_distributed_load'

    def __repr__(self) -> str:
        return f"GeneralDistributedLoad({self.start_position:.2f}-{self.end_position:.2f}m, function)"

    def __str__(self) -> str:
        return f"任意分布荷载 [{self.start_position:.2f}-{self.end_position:.2f}m]"