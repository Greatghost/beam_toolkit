"""
自由端类
"""

from typing import Tuple, Dict
from .base import Support


class FreeEnd(Support):
    """
    自由端

    特点：
    - 不约束任何位移或转角

    约束力：
    - 无约束力

    常用于悬臂梁的自由端
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化自由端

        Args:
            position: 自由端位置 (m)
            name: 名称（可选）
        """
        super().__init__(position, name or "自由端")

    def get_constraint_type(self) -> str:
        """
        获取约束类型

        Returns:
            'free'（自由端）
        """
        return 'free'

    def get_constraint_conditions(self) -> Dict[str, bool]:
        """
        获取约束条件

        Returns:
            约束条件字典（全部不约束）
        """
        return {
            'vertical_displacement': False,  # 不约束垂直位移
            'rotation': False,  # 不约束转角
            'horizontal_displacement': False,  # 不约束水平位移
        }

    def get_reaction_types(self) -> Tuple[str, ...]:
        """
        获取约束力类型

        Returns:
            ()（空元组，无约束力）
        """
        return ()

    def get_num_restraints(self) -> int:
        """
        获取约束数量

        Returns:
            0（无约束）
        """
        return 0

    def __repr__(self) -> str:
        return f"FreeEnd({self.position:.2f}m)"

    def __str__(self) -> str:
        return f"自由端 @ {self.position:.2f}m"


class GuidedSupport(Support):
    """
    导向支撑（滑动支撑）

    特点：
    - 不约束垂直位移
    - 约束转角
    - 不约束水平位移（或约束）

    约束力：
    - 反弯矩

    用于某些特殊支撑条件
    """

    def __init__(self, position: float, constrain_horizontal: bool = False, name: str = None):
        """
        初始化导向支撑

        Args:
            position: 支撑位置 (m)
            constrain_horizontal: 是否约束水平位移
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "导向支撑")
        self.constrain_horizontal = constrain_horizontal

    def get_constraint_type(self) -> str:
        """
        获取约束类型

        Returns:
            'guided'（导向支撑）
        """
        return 'guided'

    def get_constraint_conditions(self) -> Dict[str, bool]:
        """
        获取约束条件

        Returns:
            约束条件字典
        """
        return {
            'vertical_displacement': False,  # 不约束垂直位移
            'rotation': True,  # 约束转角
            'horizontal_displacement': self.constrain_horizontal,
        }

    def get_reaction_types(self) -> Tuple[str, ...]:
        """
        获取约束力类型

        Returns:
            ('moment_reaction',) 或 ('moment_reaction', 'horizontal_reaction')
        """
        if self.constrain_horizontal:
            return ('moment_reaction', 'horizontal_reaction')
        return ('moment_reaction',)

    def get_num_restraints(self) -> int:
        """
        获取约束数量

        Returns:
            1 或 2
        """
        return 2 if self.constrain_horizontal else 1

    def __repr__(self) -> str:
        return f"GuidedSupport({self.position:.2f}m, constrain_horizontal={self.constrain_horizontal})"

    def __str__(self) -> str:
        return f"导向支撑 @ {self.position:.2f}m"