"""
梁类
定义梁的基本属性和方法
"""

from typing import List, Optional, Tuple, Dict, TYPE_CHECKING
import numpy as np

from ..sections.base import Section
from ..materials.material import Material
from ..loads.base import Load
from ..supports.base import Support

if TYPE_CHECKING:
    from ..solvers.analytical_solver import AnalyticalSolver


class Beam:
    """
    类

    定义梁的几何属性、材料属性、荷载和支撑条件
    """

    def __init__(
        self,
        length: float,
        section: Section,
        material: Material,
        name: str = None
    ):
        """
        初始化梁

        Args:
            length: 梁长度 (m)
            section: 截面对象
            material: 材料对象
            name: 梁名称（可选）
        """
        if length <= 0:
            raise ValueError("梁长度必须为正值")

        self.length = length
        self.section = section
        self.material = material
        self.name = name or "梁"

        # 荷载和支撑列表
        self.loads: List[Load] = []
        self.supports: List[Support] = []

        # 求解器
        self._solver = None
        self._solved = False

        # 结果存储
        self._results = {}

    def add_load(self, load: Load) -> None:
        """
        添加荷载

        Args:
            load: 荷载对象
        """
        # 验证荷载位置
        start, end = load.get_load_range()
        if start > self.length or end > self.length:
            raise ValueError(f"荷载位置超出梁长度范围 ({self.length}m)")
        self.loads.append(load)
        self._solved = False

    def add_support(self, support: Support) -> None:
        """
        添加支撑

        Args:
            support: 支撑对象
        """
        if support.position > self.length:
            raise ValueError(f"支撑位置超出梁长度范围 ({self.length}m)")
        self.supports.append(support)
        self._solved = False

    def clear_loads(self) -> None:
        """
        清除所有荷载
        """
        self.loads.clear()
        self._solved = False

    def clear_supports(self) -> None:
        """
        清除所有支撑
        """
        self.supports.clear()
        self._solved = False

    def get_length(self) -> float:
        """
        获取梁长度

        Returns:
            梁长度 (m)
        """
        return self.length

    def get_section(self) -> Section:
        """
        获取截面

        Returns:
            截面对象
        """
        return self.section

    def get_material(self) -> Material:
        """
        获取材料

        Returns:
            材料对象
        """
        return self.material

    def get_stiffness(self) -> float:
        """
        获取梁的抗弯刚度 EI

        Returns:
            抗弯刚度 EI (N*m^2)
        """
        E = self.material.get_elastic_modulus()
        I = self.section.get_moment_of_inertia()
        return E * I

    def get_mass(self) -> float:
        """
        获取梁的质量

        Returns:
            梁质量 (kg)
        """
        density = self.material.get_density()
        if density is None:
            raise ValueError("材料未定义密度")
        area = self.section.get_area()
        return density * area * self.length

    def get_beam_type(self) -> str:
        """
        根据支撑条件判断梁的类型

        Returns:
            梁类型字符串
        """
        if len(self.supports) == 0:
            return "无支撑"

        # 检查支撑类型和位置
        support_types = [s.get_constraint_type() for s in self.supports]
        support_positions = [s.position for s in self.supports]

        # 悬臂梁：一端固定，另一端自由
        if 'fixed' in support_types:
            fixed_positions = [s.position for s in self.supports if s.get_constraint_type() == 'fixed']
            if len(fixed_positions) == 1:
                # 只有一个固定端
                if (abs(fixed_positions[0] - 0) < 1e-6 or abs(fixed_positions[0] - self.length) < 1e-6):
                    # 固定端在端点
                    return "悬臂梁"

        # 简支梁：两端简支
        if 'simple' in support_types:
            simple_positions = [s.position for s in self.supports if s.get_constraint_type() == 'simple']
            if len(simple_positions) >= 2:
                # 有简支在两端
                if (abs(min(simple_positions) - 0) < 1e-6 and
                    abs(max(simple_positions) - self.length) < 1e-6):
                    return "简支梁"

        # 外伸梁：支撑不在两端
        if 'simple' in support_types:
            simple_positions = [s.position for s in self.supports if s.get_constraint_type() == 'simple']
            for pos in simple_positions:
                if pos > 0.01 and pos < self.length - 0.01:
                    return "外伸梁"

        # 固定-简支梁（一端固定，另一端简支）
        if 'fixed' in support_types and 'simple' in support_types:
            return "固定-简支梁"

        # 两端固定梁
        if len([s for s in self.supports if s.get_constraint_type() == 'fixed']) == 2:
            return "两端固定梁"

        return "复杂支撑梁"

    def solve(self, num_points: int = 100, solver_type: str = 'analytical') -> Dict:
        """
        求解梁的内力和变形

        Args:
            num_points: 计算点数
            solver_type: 求解器类型

        Returns:
            包含内力、应力、变形结果的字典
        """
        if solver_type == 'analytical':
            from ..solvers.analytical_solver import AnalyticalSolver
            self._solver = AnalyticalSolver(self, num_points)
        else:
            raise ValueError(f"不支持的求解器类型: {solver_type}")

        self._results = self._solver.solve()
        self._solved = True

        return self._results

    def get_reaction_forces(self) -> Dict:
        """
        获取支座反力

        Returns:
            支座反力字典
        """
        if not self._solved:
            self.solve()
        return self._results.get('reactions', {})

    def get_internal_forces(self) -> Dict:
        """
        获取内力分布

        Returns:
            内力结果字典，包含位置、弯矩、剪力数组
        """
        if not self._solved:
            self.solve()
        return self._results.get('internal_forces', {})

    def get_stresses(self) -> Dict:
        """
        获取应力分布

        Returns:
            应力结果字典
        """
        if not self._solved:
            self.solve()
        return self._results.get('stresses', {})

    def get_deformations(self) -> Dict:
        """
        获取变形分布

        Returns:
            变形结果字典，包含位置、挠度、转角数组
        """
        if not self._solved:
            self.solve()
        return self._results.get('deformations', {})

    def get_max_bending_moment(self) -> Tuple[float, float]:
        """
        获取最大弯矩及其位置

        Returns:
            (最大弯矩绝对值, 位置) (N*m, m)
        """
        if not self._solved:
            self.solve()

        internal_forces = self._results['internal_forces']
        M = internal_forces['moment']
        x = internal_forces['position']

        max_M = np.max(np.abs(M))
        max_pos = x[np.argmax(np.abs(M))]

        return (max_M, max_pos)

    def get_max_shear_force(self) -> Tuple[float, float]:
        """
        获取最大剪力及其位置

        Returns:
            (最大剪力绝对值, 位置) (N, m)
        """
        if not self._solved:
            self.solve()

        internal_forces = self._results['internal_forces']
        V = internal_forces['shear']
        x = internal_forces['position']

        max_V = np.max(np.abs(V))
        max_pos = x[np.argmax(np.abs(V))]

        return (max_V, max_pos)

    def get_max_deflection(self) -> Tuple[float, float]:
        """
        获取最大挠度及其位置

        Returns:
            (最大挠度绝对值, 位置) (m, m)
        """
        if not self._solved:
            self.solve()

        deformations = self._results['deformations']
        v = deformations['deflection']
        x = deformations['position']

        max_v = np.max(np.abs(v))
        max_pos = x[np.argmax(np.abs(v))]

        return (max_v, max_pos)

    def check_safety(self) -> Dict:
        """
        检查梁的安全性

        Returns:
            安全性检查结果字典
        """
        if not self._solved:
            self.solve()

        # 获取最大应力
        stresses = self._results['stresses']
        max_bending_stress = np.max(np.abs(stresses['bending_stress']))
        max_shear_stress = np.max(np.abs(stresses['shear_stress']))

        # 获取许用应力
        allowable_stress = self.material.get_allowable_stress()

        # 计算安全系数
        bending_safety_factor = allowable_stress / max_bending_stress if max_bending_stress > 0 else float('inf')
        shear_safety_factor = allowable_stress / max_shear_stress * 2 if max_shear_stress > 0 else float('inf')

        # 检查变形
        max_deflection = self.get_max_deflection()[0]
        deflection_limit = self.length / 250  # 常用限值：L/250
        deflection_safe = max_deflection <= deflection_limit

        return {
            'max_bending_stress': max_bending_stress,
            'max_shear_stress': max_shear_stress,
            'allowable_stress': allowable_stress,
            'bending_safety_factor': bending_safety_factor,
            'shear_safety_factor': shear_safety_factor,
            'is_safe': bending_safety_factor >= 1.0,
            'max_deflection': max_deflection,
            'deflection_limit': deflection_limit,
            'deflection_safe': deflection_safe,
        }

    def get_info(self) -> str:
        """
        获取梁的信息摘要

        Returns:
            信息字符串
        """
        info_lines = [
            f"梁名称: {self.name}",
            f"长度: {self.length:.3f} m",
            f"截面: {self.section}",
            f"材料: {self.material}",
            f"抗弯刚度 EI: {self.get_stiffness():.2e} N*m^2",
            f"梁类型: {self.get_beam_type()}",
            f"荷载数量: {len(self.loads)}",
            f"支撑数量: {len(self.supports)}",
        ]

        if self._solved:
            max_M, pos_M = self.get_max_bending_moment()
            max_V, pos_V = self.get_max_shear_force()
            max_v, pos_v = self.get_max_deflection()

            info_lines.extend([
                f"",
                f"=== 计算结果 ===",
                f"最大弯矩: {max_M:.2f} N*m @ {pos_M:.2f} m",
                f"最大剪力: {max_V:.2f} N @ {pos_V:.2f} m",
                f"最大挠度: {max_v:.6f} m ({max_v/self.length*1000:.4f}/1000L) @ {pos_v:.2f} m",
            ])

            safety = self.check_safety()
            info_lines.extend([
                f"",
                f"=== 安全性检查 ===",
                f"最大弯曲应力: {safety['max_bending_stress']/1e6:.2f} MPa",
                f"许用应力: {safety['allowable_stress']/1e6:.2f} MPa",
                f"安全系数: {safety['bending_safety_factor']:.2f}",
                f"安全状态: {'通过' if safety['is_safe'] else '不安全'}",
            ])

        return '\n'.join(info_lines)

    def __repr__(self) -> str:
        return f"Beam({self.name}, L={self.length:.2f}m, {self.section.name}, {self.material.name})"

    def __str__(self) -> str:
        return f"{self.name}: {self.length:.2f}m长, {self.get_beam_type()}"