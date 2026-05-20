"""
简支支撑类
"""

from typing import Tuple, Dict
from .base import Support


class SimpleSupport(Support):
    """
    简支支撑（滚动支撑）

    特点：
    - 约束垂直位移
    - 不约束转角
    - 不约束水平位移

    约束力：
    - 垂直反力（剪力）
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化简支支撑

        Args:
            position: 支撑位置 (m)
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "简支")

    def get_constraint_type(self) -> str:
        """
        获取约束类型

        Returns:
            'simple'（简支）
        """
        return 'simple'

    def get_constraint_conditions(self) -> Dict[str, bool]:
        """
        获取约束条件

        Returns:
            约束条件字典
        """
        return {
            'vertical_displacement': True,  # 约束垂直位移
            'rotation': False,  # 不约束转角
            'horizontal_displacement': False,  # 不约束水平位移
        }

    def get_reaction_types(self) -> Tuple[str, ...]:
        """
        获取约束力类型

        Returns:
            ('vertical_reaction',)
        """
        return ('vertical_reaction',)

    def get_num_restraints(self) -> int:
        """
        获取约束数量

        Returns:
            1（一个约束）
        """
        return 1

    def __repr__(self) -> str:
        return f"SimpleSupport({self.position:.2f}m)"

    def __str__(self) -> str:
        return f"简支支撑 @ {self.position:.2f}m"


class RollerSupport(SimpleSupport):
    """
    滚动支撑

    与简支支撑相同，允许水平移动
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化滚动支撑

        Args:
            position: 支撑位置 (m)
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "滚动支撑")


class PinnedSupport(Support):
    """
    铰支撑

    特点：
    - 约束垂直位移
    - 不约束转角
    - 约束水平位移

    约束力：
    - 垂直反力
    - 水平反力

    常用于梁与柱的连接点
    """

    def __init__(self, position: float, name: str = None):
        """
        初始化铰支撑

        Args:
            position: 支撑位置 (m)
            name: 支撑名称（可选）
        """
        super().__init__(position, name or "铰支撑")

    def get_constraint_type(self) -> str:
        """
        获取约束类型

        Returns:
            'pinned'（铰支撑）
        """
        return 'pinned'

    def get_constraint_conditions(self) -> Dict[str, bool]:
        """
        获取约束条件

        Returns:
            约束条件字典
        """
        return {
            'vertical_displacement': True,  # 约束垂直位移
            'rotation': False,  # 不约束转角
            'horizontal_displacement': True,  # 约束水平位移
        }

    def get_reaction_types(self) -> Tuple[str, ...]:
        """
        获取约束力类型

        Returns:
            ('vertical_reaction', 'horizontal_reaction')
        """
        return ('vertical_reaction', 'horizontal_reaction')

    def get_num_restraints(self) -> int:
        """
        获取约束数量

        Returns:
            2（两个约束）
        """
        return 2

    def __repr__(self) -> str:
        return f"PinnedSupport({self.position:.2f}m)"

    def __str__(self) -> str:
        return f"铰支撑 @ {self.position:.2f}m"