"""
固定端支撑类
"""

from typing import Tuple, Dict
from .base import Support


class FixedSupport(Support):
    """
    固定端支撑

    特点：
    - 约束垂直位移
    - 约束转角
    - 约束水平位移

    约束力：
    - 垂直反力（剪力）
    - 反弯矩
    - 水平反力（轴力）
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化固定端支撑

        Args:
            position: 支撑位置 (m)
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "固定端")

    def get_constraint_type(self) -> str:
        """
        获取约束类型

        Returns:
            'fixed'（固定端）
        """
        return 'fixed'

    def get_constraint_conditions(self) -> Dict[str, bool]:
        """
        获取约束条件

        Returns:
            约束条件字典（全部约束）
        """
        return {
            'vertical_displacement': True,  # 约束垂直位移
            'rotation': True,  # 约束转角
            'horizontal_displacement': True,  # 约束水平位移
        }

    def get_reaction_types(self) -> Tuple[str, ...]:
        """
        获取约束力类型

        Returns:
            ('vertical_reaction', 'moment_reaction', 'horizontal_reaction')
        """
        return ('vertical_reaction', 'moment_reaction', 'horizontal_reaction')

    def get_num_restraints(self) -> int:
        """
        获取约束数量

        Returns:
            3（三个约束）
        """
        return 3

    def __repr__(self) -> str:
        return f"FixedSupport({self.position:.2f}m)"

    def __str__(self) -> str:
        return f"固定端 @ {self.position:.2f}m"


class ClampedSupport(FixedSupport):
    """
    夹紧支撑（固定端的另一种称呼）

    与固定端相同
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化夹紧支撑

        Args:
            position: 支撑位置 (m)
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "夹紧端")


class FixedEnd(FixedSupport):
    """
    固定端（固定支撑的另一种称呼）

    与固定支撑相同，常用于悬臂梁的一端
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化固定端

        Args:
            position: 支撑位置 (m)
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "固定端")