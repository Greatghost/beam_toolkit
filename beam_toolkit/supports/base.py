"""
支撑基类
定义边界条件的基本属性和方法
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict


class Support(ABC):
    """
    支撑基类（边界条件）

    所有支撑类型必须继承此类并实现其抽象方法
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化支撑

        Args:
            position: 支撑位置（从梁左端算起）(m)
            name: 支撑名称（可选）
        """
        if position < 0:
            raise ValueError("支撑位置必须为非负值")

        self.position = position
        self.name = name or self.__class__.__name__

    @abstractmethod
    def get_constraint_type(self) -> str:
        """
        获取约束类型

        Returns:
            约束类型字符串
        """
        pass

    @abstractmethod
    def get_constraint_conditions(self) -> Dict[str, bool]:
        """
        获取约束条件

        Returns:
            包含各方向约束状态的字典:
            - 'vertical_displacement': 垂直位移约束（True/False）
            - 'rotation': 转角约束（True/False）
            - 'horizontal_displacement': 水平位移约束（True/False）
        """
        pass

    @abstractmethod
    def get_reaction_types(self) -> Tuple[str, ...]:
        """
        获取约束力类型

        Returns:
            约束力类型元组
        """
        pass

    def get_position(self) -> float:
        """
        获取支撑位置

        Returns:
            支撑位置 (m)
        """
        return self.position

    def has_vertical_constraint(self) -> bool:
        """
        是否有垂直位移约束

        Returns:
            是否约束垂直位移
        """
        return self.get_constraint_conditions()['vertical_displacement']

    def has_rotation_constraint(self) -> bool:
        """
        是否有转角约束

        Returns:
            是否约束转角
        """
        return self.get_constraint_conditions()['rotation']

    def has_horizontal_constraint(self) -> bool:
        """
        是否有水平位移约束

        Returns:
            是否约束水平位移
        """
        return self.get_constraint_conditions()['horizontal_displacement']

    def __repr__(self) -> str:
        return f"{self.name}({self.position:.2f}m)"

    def __str__(self) -> str:
        return f"{self.name} @ {self.position:.2f}m, {self.get_constraint_type()}"