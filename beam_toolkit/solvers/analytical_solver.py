"""
解析求解器
使用解析方法求解梁的内力和变形
"""

from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Any
import numpy as np
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..core.beam import Beam

from ..loads.point_load import PointLoad
from ..loads.distributed_load import UniformDistributedLoad, LinearDistributedLoad
from ..loads.moment_load import MomentLoad
from ..supports.fixed_support import FixedSupport
from ..supports.simple_support import SimpleSupport


class SolverBase(ABC):
    """
    求解器基类
    """

    def __init__(self, beam: Any, num_points: int = 100):
        """
        初始化求解器

        Args:
            beam: 梁对象
            num_points: 计算点数
        """
        self.beam = beam
        self.num_points = num_points
        self.x = np.linspace(0, beam.length, num_points)

    @abstractmethod
    def solve(self) -> Dict:
        """
        求解梁的内力和变形

        Returns:
            包含结果的字典
        """
        pass


class AnalyticalSolver(SolverBase):
    """
    解析求解器

    使用解析方法求解简支梁、悬臂梁等常见梁型的内力和变形
    """

    def __init__(self, beam: Beam, num_points: int = 100):
        """
        初始化解析求解器

        Args:
            beam: 梁对象
            num_points: 计算点数
        """
        super().__init__(beam, num_points)
        self._reactions = {}
        self._M = np.zeros(num_points)  # 弯矩
        self._V = np.zeros(num_points)  # 剪力
        self._v = np.zeros(num_points)  # 挠度
        self._theta = np.zeros(num_points)  # 转角

    def solve(self) -> Dict:
        """
        求解梁的内力和变形

        Returns:
            结果字典
        """
        beam_type = self.beam.get_beam_type()

        # 根据梁类型选择求解方法
        if beam_type == "悬臂梁":
            self._solve_cantilever()
        elif beam_type == "简支梁":
            self._solve_simple_beam()
        elif beam_type == "两端固定梁":
            self._solve_fixed_fixed_beam()
        elif beam_type == "固定-简支梁":
            self._solve_fixed_simple_beam()
        else:
            # 使用数值积分方法
            self._solve_numerical()

        # 计算应力
        stresses = self._calculate_stresses()

        # 组装结果
        results = {
            'reactions': self._reactions,
            'internal_forces': {
                'position': self.x,
                'moment': self._M,
                'shear': self._V,
            },
            'stresses': stresses,
            'deformations': {
                'position': self.x,
                'deflection': self._v,
                'rotation': self._theta,
            },
        }

        return results

    def _solve_cantilever(self) -> None:
        """
        求解悬臂梁

        固定端在一端，自由端在另一端
        """
        # 找到固定端位置
        fixed_support = None
        for support in self.beam.supports:
            if support.get_constraint_type() == 'fixed':
                fixed_support = support
                break

        if fixed_support is None:
            raise ValueError("悬臂梁必须有固定端")

        L = self.beam.length
        E = self.beam.material.get_elastic_modulus()
        I = self.beam.section.get_moment_of_inertia()
        EI = E * I

        # 固定端位置（假设在左端）
        fixed_at_left = fixed_support.position < L / 2

        # 计算支座反力
        total_force = 0.0
        total_moment_at_fixed = 0.0

        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                total_force += load.magnitude
                if fixed_at_left:
                    # 固定端在左端
                    moment_arm = load.position
                    total_moment_at_fixed += load.magnitude * moment_arm
                else:
                    # 固定端在右端
                    moment_arm = L - load.position
                    total_moment_at_fixed += load.magnitude * moment_arm

            elif isinstance(load, UniformDistributedLoad):
                w = load.magnitude
                a = load.start_position
                b = load.end_position
                load_length = b - a
                total_force += w * load_length

                # 分布力对固定端的矩
                if fixed_at_left:
                    equivalent_position = a + load_length / 2
                    total_moment_at_fixed += w * load_length * equivalent_position
                else:
                    equivalent_position = L - (a + load_length / 2)
                    total_moment_at_fixed += w * load_length * equivalent_position

            elif isinstance(load, MomentLoad):
                total_moment_at_fixed += load.magnitude

        # 支座反力
        if fixed_at_left:
            self._reactions = {
                'position': 0.0,
                'vertical_reaction': -total_force,  # 向上
                'moment_reaction': -total_moment_at_fixed,  # 反弯矩
            }
        else:
            self._reactions = {
                'position': L,
                'vertical_reaction': total_force,  # 向上
                'moment_reaction': total_moment_at_fixed,  # 反弯矩
            }

        # 计算内力和变形
        for i, xi in enumerate(self.x):
            self._calculate_cantilever_internal(xi, fixed_at_left, L, EI)

    def _calculate_cantilever_internal(self, x: float, fixed_at_left: bool, L: float, EI: float) -> Tuple[float, float, float, float]:
        """
        计算悬臂梁在指定位置的内力和变形

        Args:
            x: 位置
            fixed_at_left: 固定端是否在左端
            L: 梁长度
            EI: 抗弯刚度

        Returns:
            (剪力, 弯矩, 挠度, 转角)
        """
        V = 0.0
        M = 0.0
        v = 0.0
        theta = 0.0

        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                V_load, M_load, v_load, theta_load = self._point_load_cantilever(
                    load, x, fixed_at_left, L, EI
                )
                V += V_load
                M += M_load
                v += v_load
                theta += theta_load

            elif isinstance(load, UniformDistributedLoad):
                V_load, M_load, v_load, theta_load = self._udl_cantilever(
                    load, x, fixed_at_left, L, EI
                )
                V += V_load
                M += M_load
                v += v_load
                theta += theta_load

            elif isinstance(load, MomentLoad):
                M_load, v_load, theta_load = self._moment_load_cantilever(
                    load, x, fixed_at_left, L, EI
                )
                M += M_load
                v += v_load
                theta += theta_load

        # 存储结果（需要找到对应的索引）
        idx = int(x / L * (self.num_points - 1))
        if idx < self.num_points:
            self._V[idx] = V
            self._M[idx] = M
            self._v[idx] = v
            self._theta[idx] = theta

        return (V, M, v, theta)

    def _point_load_cantilever(self, load: PointLoad, x: float, fixed_at_left: bool, L: float, EI: float) -> Tuple[float, float, float, float]:
        """
        集中力对悬臂梁的作用
        """
        P = load.magnitude
        a = load.position

        if fixed_at_left:
            # 固定端在左端 (x=0)
            if x <= a:
                # 荷载作用点之前
                V = -P
                M = -P * (a - x)
                # 挠度公式（考虑边界条件）
                v = -P * (a - x) ** 2 * (3 * a - (a - x)) / (6 * EI) if x < a else 0
                # 对于悬臂梁的正确挠度公式
                if a <= L:
                    # v = P * x^2 * (3a - x) / (6EI) for 0 <= x <= a
                    # v = P * a^2 * (3x - a) / (6EI) for a <= x <= L
                    if x <= a:
                        v = -P * x ** 2 * (3 * a - x) / (6 * EI)
                        theta = -P * x * (2 * a - x) / (2 * EI)
                    else:
                        v = -P * a ** 2 * (3 * x - a) / (6 * EI)
                        theta = -P * a ** 2 / (2 * EI)
                else:
                    v = 0
                    theta = 0
            else:
                # 荷载作用点之后
                V = 0
                M = 0
                v = -P * a ** 2 * (3 * x - a) / (6 * EI)
                theta = -P * a ** 2 / (2 * EI)
        else:
            # 固定端在右端 (x=L)
            if x >= a:
                V = P
                M = P * (x - a)
                xi = L - x
                ai = L - a
                if xi <= ai:
                    v = -P * xi ** 2 * (3 * ai - xi) / (6 * EI)
                    theta = P * xi * (2 * ai - xi) / (2 * EI)
                else:
                    v = -P * ai ** 2 * (3 * xi - ai) / (6 * EI)
                    theta = P * ai ** 2 / (2 * EI)
            else:
                V = 0
                M = 0
                xi = L - x
                ai = L - a
                v = -P * ai ** 2 * (3 * xi - ai) / (6 * EI)
                theta = P * ai ** 2 / (2 * EI)

        return (V, M, v, theta)

    def _udl_cantilever(self, load: UniformDistributedLoad, x: float, fixed_at_left: bool, L: float, EI: float) -> Tuple[float, float, float, float]:
        """
        均布荷载对悬臂梁的作用
        """
        w = load.magnitude  # 向下为正
        a = load.start_position
        b = load.end_position

        V = 0.0
        M = 0.0
        v = 0.0
        theta = 0.0

        if fixed_at_left:
            # 固定端在左端
            if b <= x:
                # x在荷载范围之后，全部荷载有效
                V = -w * (b - a)
                M = -w * (b - a) * (x - a - (b - a) / 2)
            elif a <= x < b:
                # x在荷载范围内
                V = -w * (x - a)
                M = -w * (x - a) ** 2 / 2
            else:
                V = 0
                M = 0

            # 挠度计算（简化处理）
            if a == 0 and b == L:
                # 全跨均布荷载
                v = -w * x ** 2 * (6 * L ** 2 - 4 * L * x + x ** 2) / (24 * EI)
                theta = -w * x * (3 * L ** 2 - 3 * L * x + x ** 2) / (6 * EI)
            else:
                # 部分均布荷载（使用叠加原理）
                # 简化处理，取等效集中力
                P_eq = w * (b - a)
                pos_eq = a + (b - a) / 2
                V_p, M_p, v_p, theta_p = self._point_load_cantilever(
                    PointLoad(pos_eq, P_eq), x, fixed_at_left, L, EI
                )
                # 这是近似值，实际应该用积分公式
                v = v_p * (b - a) / 2  # 简化修正
                theta = theta_p * (b - a) / 2

        else:
            # 固定端在右端
            xi = L - x
            ai = L - a
            bi = L - b

            if bi >= xi:
                # xi在荷载范围之后
                V = w * (a - b)
                M = w * (a - b) * (xi - bi - (ai - bi) / 2)
            elif bi < xi <= ai:
                # xi在荷载范围内
                V = w * (xi - bi)
                M = w * (xi - bi) ** 2 / 2
            else:
                V = 0
                M = 0

            # 挠度计算（简化）
            if a == 0 and b == L:
                v = -w * xi ** 2 * (6 * L ** 2 - 4 * L * xi + xi ** 2) / (24 * EI)
                theta = w * xi * (3 * L ** 2 - 3 * L * xi + xi ** 2) / (6 * EI)

        return (V, M, v, theta)

    def _moment_load_cantilever(self, load: MomentLoad, x: float, fixed_at_left: bool, L: float, EI: float) -> Tuple[float, float, float]:
        """
        集中弯矩对悬臂梁的作用
        """
        M0 = load.magnitude
        a = load.position

        M = 0.0
        v = 0.0
        theta = 0.0

        if fixed_at_left:
            if x <= a:
                M = -M0
            # 挠度
            if a <= L:
                if x <= a:
                    v = -M0 * x ** 2 / (2 * EI)
                    theta = -M0 * x / EI
                else:
                    v = -M0 * a ** 2 / (2 * EI) - M0 * a * (x - a) / EI
                    theta = -M0 * a / EI
        else:
            xi = L - x
            ai = L - a
            if x >= a:
                M = M0
            if ai <= L:
                if xi <= ai:
                    v = -M0 * xi ** 2 / (2 * EI)
                    theta = M0 * xi / EI
                else:
                    v = -M0 * ai ** 2 / (2 * EI) - M0 * ai * (xi - ai) / EI
                    theta = M0 * ai / EI

        return (M, v, theta)

    def _solve_simple_beam(self) -> None:
        """
        求解简支梁
        """
        L = self.beam.length
        E = self.beam.material.get_elastic_modulus()
        I = self.beam.section.get_moment_of_inertia()
        EI = E * I

        # 计算支座反力
        # 假设左支座在x=0，右支座在x=L
        R_left = 0.0
        R_right = 0.0

        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                P = load.magnitude
                a = load.position
                # 向下荷载P为正值，反力向上为负值（平衡）
                R_left -= P * (L - a) / L
                R_right -= P * a / L

            elif isinstance(load, UniformDistributedLoad):
                w = load.magnitude  # 向下为正
                a = load.start_position
                b = load.end_position
                load_length = b - a
                equivalent_pos = a + load_length / 2
                total_load = w * load_length
                R_left -= total_load * (L - equivalent_pos) / L
                R_right -= total_load * equivalent_pos / L

            elif isinstance(load, MomentLoad):
                # 简支梁上作用的集中弯矩
                M0 = load.magnitude
                a = load.position
                # 顺时针弯矩（正值）产生的反力
                R_left -= M0 / L
                R_right += M0 / L

        self._reactions = {
            'left': {'position': 0.0, 'reaction': -R_left},  # 反力向上为正
            'right': {'position': L, 'reaction': -R_right},
        }

        # 计算内力和变形 - 使用改进的方法处理剪力突变
        # 首先收集所有集中力作用点
        point_load_positions = []
        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                point_load_positions.append(load.position)

        # 计算每个位置的内力
        for i, xi in enumerate(self.x):
            V, M, v, theta = self._calculate_simple_beam_internal_improved(xi, L, EI, R_left, R_right)
            self._V[i] = V
            self._M[i] = M
            self._v[i] = v
            self._theta[i] = theta

    def _calculate_simple_beam_internal(self, x: float, L: float, EI: float, R_left: float) -> Tuple[float, float, float, float]:
        """
        计算简支梁在指定位置的内力和变形
        """
        V = R_left  # 初始剪力
        M = R_left * x  # 初始弯矩
        v = R_left * x ** 3 / (6 * EI)  # 初始挠度（不含边界条件修正）
        theta = R_left * x ** 2 / (2 * EI)

        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                V_load, M_load, v_load, theta_load = self._point_load_simple(
                    load, x, L, EI
                )
                V += V_load
                M += M_load
                v += v_load
                theta += theta_load

            elif isinstance(load, UniformDistributedLoad):
                V_load, M_load, v_load, theta_load = self._udl_simple(
                    load, x, L, EI
                )
                V += V_load
                M += M_load
                v += v_load
                theta += theta_load

            elif isinstance(load, MomentLoad):
                M_load, v_load, theta_load = self._moment_load_simple(
                    load, x, L, EI
                )
                M += M_load
                v += v_load
                theta += theta_load

        # 简支梁边界条件修正（挠度在两端为零）
        # 使用叠加方法，加入修正项
        # 基本挠度 v_basic，需要修正使其满足边界条件
        # 修正项：v_correction = A*x + B*x^3，其中A和B由边界条件确定
        # 对于简支梁：修正项 = (v(L)/L) * x - (v(L)/(6*L*EI)) * x^3，这里简化处理

        # 简化：使用标准边界条件处理
        # 实际上需要对每种荷载单独应用边界条件

        return (V, M, v, theta)

    def _calculate_simple_beam_internal_improved(self, x: float, L: float, EI: float, R_left: float, R_right: float) -> Tuple[float, float, float, float]:
        """
        改进的简支梁内力计算方法
        正确处理集中力处的剪力突变

        用户弯矩符号规则：顺时针弯矩为正（使梁上表面受拉）
        对应于常规力学中的负弯矩

        用户剪力符号规则：使截面顺时针转动的剪力为正

        计算方法：
        1. 用常规方法计算弯矩（下表面受拉为正）
        2. 反转符号以符合用户规则（下表面受拉变为负）
        """
        # 反力大小（向上）
        R_A = -R_left  # 转换为正值

        # 常规剪力计算（向上力使截面产生负剪力）
        V_conventional = -R_A
        # 用户规则剪力：需要反转吗？向上力产生逆时针剪力 = 负值
        V = V_conventional  # 保持一致

        # 常规弯矩计算（下表面受拉为正）
        # 对于 x < a: M = R_A * x（正值，下表面受拉）
        # 对于 x > a: M = R_A * x - P * (x - a)
        M_conventional = R_A * x

        v = 0.0
        theta = 0.0

        # 逐个考虑荷载的影响
        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                P = load.magnitude  # 向下为正
                a = load.position

                # 集中力对剪力的影响：在作用点之后剪力有突变
                if x > a:
                    V += P  # 向下力使剪力增加（正值）
                    M_conventional -= P * (x - a)  # 向下力减小常规弯矩

                # 挠度计算
                if x <= a:
                    v += -P * (L - a) * x * (L**2 - (L-a)**2 - x**2) / (6 * EI * L)
                    theta += -P * (L - a) * (L**2 - (L-a)**2 - 3*x**2) / (6 * EI * L)
                else:
                    v += -P * a * (L - x) * (L**2 - a**2 - (L-x)**2) / (6 * EI * L)
                    theta += P * a * (L**2 - a**2 - 3*(L-x)**2) / (6 * EI * L)

            elif isinstance(load, UniformDistributedLoad):
                w = load.magnitude  # 向下为正
                a = load.start_position
                b = load.end_position

                # 均布荷载对剪力和弯矩的影响
                if a == 0 and b == L:
                    # 全跨均布荷载
                    V += w * x  # 向下荷载使剪力增加
                    M_conventional -= w * x**2 / 2  # 减小常规弯矩

                    # 挠度
                    v += -w * x * (L**3 - 2*L*x**2 + x**3) / (24 * EI)
                    theta += -w * (L**3 - 6*L*x**2 + 4*x**3) / (24 * EI)
                else:
                    # 部分均布荷载
                    if x > a:
                        if x <= b:
                            V += w * (x - a)
                            M_conventional -= w * (x - a)**2 / 2
                        else:
                            V += w * (b - a)
                            M_conventional -= w * (b - a) * (x - a - (b - a)/2)

            elif isinstance(load, MomentLoad):
                M0 = load.magnitude  # 顺时针为正
                a = load.position

                # 集中弯矩的影响
                if x > a:
                    # 顺时针弯矩增加常规弯矩（但用户规则中，顺时针为正）
                    M_conventional += M0

                # 挠度计算
                if x <= a:
                    v += -M0 * x * (L - a) * (L**2 - x**2 - (L-a)**2) / (6 * EI * L)
                    theta += -M0 * (L - a) * (L**2 - 3*x**2 - (L-a)**2) / (6 * EI * L)
                else:
                    v += M0 * (L - x) * a * (L**2 - (L-x)**2 - a**2) / (6 * EI * L)
                    theta += M0 * a * (L**2 - 3*(L-x)**2 - a**2) / (6 * EI * L)

        # 转换为用户规则的弯矩符号
        # 用户规则：顺时针弯矩为正（上表面受拉）
        # 常规弯矩（下表面受拉为正）需要反转
        M = -M_conventional

        return (V, M, v, theta)

    def _point_load_simple(self, load: PointLoad, x: float, L: float, EI: float) -> Tuple[float, float, float, float]:
        """
        集中力对简支梁的作用
        """
        P = load.magnitude
        a = load.position

        V = 0.0
        M = 0.0
        v = 0.0
        theta = 0.0

        if x < a:
            V = -P * (L - a) / L
            M = -P * (L - a) * x / L
            v = -P * (L - a) * x * (L ** 2 - (L - a) ** 2 - x ** 2) / (6 * EI * L)
            theta = -P * (L - a) * (L ** 2 - (L - a) ** 2 - 3 * x ** 2) / (6 * EI * L)
        else:
            V = -P * a / L
            M = -P * a * (L - x) / L
            # 挠度公式
            v = -P * a * (L - x) * (L ** 2 - a ** 2 - (L - x) ** 2) / (6 * EI * L)
            theta = P * a * (L ** 2 - a ** 2 - 3 * (L - x) ** 2) / (6 * EI * L)

        return (V, M, v, theta)

    def _udl_simple(self, load: UniformDistributedLoad, x: float, L: float, EI: float) -> Tuple[float, float, float, float]:
        """
        均布荷载对简支梁的作用
        """
        w = load.magnitude
        a = load.start_position
        b = load.end_position

        V = 0.0
        M = 0.0
        v = 0.0
        theta = 0.0

        if a == 0 and b == L:
            # 全跨均布荷载
            V = -w * (L / 2 - x)
            M = -w * x * (L - x) / 2
            v = -w * x * (L ** 3 - 2 * L * x ** 2 + x ** 3) / (24 * EI)
            theta = -w * (L ** 3 - 6 * L * x ** 2 + 4 * x ** 3) / (24 * EI)
        else:
            # 部分均布荷载
            # 简化处理：将分布荷载视为多个集中力的叠加
            n_segments = 10
            segment_length = (b - a) / n_segments
            for j in range(n_segments):
                seg_start = a + j * segment_length
                seg_end = a + (j + 1) * segment_length
                seg_mid = seg_start + segment_length / 2
                P_seg = w * segment_length

                V_seg, M_seg, v_seg, theta_seg = self._point_load_simple(
                    PointLoad(seg_mid, P_seg), x, L, EI
                )
                V += V_seg
                M += M_seg
                v += v_seg
                theta += theta_seg

        return (V, M, v, theta)

    def _moment_load_simple(self, load: MomentLoad, x: float, L: float, EI: float) -> Tuple[float, float, float]:
        """
        集中弯矩对简支梁的作用
        """
        M0 = load.magnitude
        a = load.position

        M = 0.0
        v = 0.0
        theta = 0.0

        if x < a:
            M = -M0 * x / L
            v = -M0 * x * (L - a) * (L ** 2 - x ** 2 - (L - a) ** 2) / (6 * EI * L)
            theta = -M0 * (L - a) * (L ** 2 - 3 * x ** 2 - (L - a) ** 2) / (6 * EI * L)
        else:
            M = -M0 * (L - x) / L
            v = M0 * (L - x) * a * (L ** 2 - (L - x) ** 2 - a ** 2) / (6 * EI * L)
            theta = M0 * a * (L ** 2 - 3 * (L - x) ** 2 - a ** 2) / (6 * EI * L)

        return (M, v, theta)

    def _solve_fixed_fixed_beam(self) -> None:
        """
        求解两端固定梁
        """
        L = self.beam.length
        E = self.beam.material.get_elastic_modulus()
        I = self.beam.section.get_moment_of_inertia()
        EI = E * I

        # 计算支座反力（两端固定梁）
        # 固端弯矩和固端剪力
        M_A = 0.0  # 左端固端弯矩
        M_B = 0.0  # 右端固端弯矩
        V_A = 0.0  # 左端固端剪力
        V_B = 0.0  # 右端固端剪力

        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                P = load.magnitude
                a = load.position
                b = L - a
                # 固端弯矩
                M_A += P * a * b ** 2 / L ** 2
                M_B += P * b * a ** 2 / L ** 2
                # 固端剪力
                V_A += P * b ** 2 * (L + 2 * a) / L ** 3
                V_B += P * a ** 2 * (L + 2 * b) / L ** 3

            elif isinstance(load, UniformDistributedLoad):
                if load.start_position == 0 and load.end_position == L:
                    w = load.magnitude
                    M_A += w * L ** 2 / 12
                    M_B += w * L ** 2 / 12
                    V_A += w * L / 2
                    V_B += w * L / 2

        self._reactions = {
            'left': {
                'position': 0.0,
                'vertical_reaction': V_A,
                'moment_reaction': -M_A,
            },
            'right': {
                'position': L,
                'vertical_reaction': V_B,
                'moment_reaction': M_B,
            },
        }

        # 计算内力和变形（简化处理）
        for i, xi in enumerate(self.x):
            V = V_A
            M = V_A * xi - M_A

            # 考虑荷载的影响
            for load in self.beam.loads:
                if isinstance(load, PointLoad):
                    if xi > load.position:
                        V -= load.magnitude
                        M -= load.magnitude * (xi - load.position)

                elif isinstance(load, UniformDistributedLoad):
                    if load.start_position == 0 and load.end_position == L:
                        w = load.magnitude
                        V -= w * xi
                        M -= w * xi ** 2 / 2

            self._V[i] = V
            self._M[i] = M

            # 挠度计算（使用叠加原理）
            # 两端固定梁的挠度较小
            v = 0.0
            for load in self.beam.loads:
                if isinstance(load, UniformDistributedLoad):
                    if load.start_position == 0 and load.end_position == L:
                        w = load.magnitude
                        v = w * xi ** 2 * (L - xi) ** 2 / (24 * EI)

            self._v[i] = v

            # 转角
            theta = 0.0
            for load in self.beam.loads:
                if isinstance(load, UniformDistributedLoad):
                    if load.start_position == 0 and load.end_position == L:
                        w = load.magnitude
                        theta = w * xi * (L - xi) * (L - 2 * xi) / (12 * EI)

            self._theta[i] = theta

    def _solve_fixed_simple_beam(self) -> None:
        """
        求解一端固定一端简支梁
        """
        L = self.beam.length
        E = self.beam.material.get_elastic_modulus()
        I = self.beam.section.get_moment_of_inertia()
        EI = E * I

        # 假设左端固定，右端简支
        M_A = 0.0  # 固端弯矩
        V_A = 0.0  # 固端剪力
        V_B = 0.0  # 简支端剪力

        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                P = load.magnitude
                a = load.position
                # 固端弯矩
                M_A += P * a * (L - a) * (2 * L - a) / (2 * L ** 2)
                # 支座反力
                V_A += P * (L - a) ** 2 * (L + 2 * a) / (2 * L ** 3)
                V_B += P * a ** 2 * (3 * L - 2 * a) / (2 * L ** 3)

            elif isinstance(load, UniformDistributedLoad):
                if load.start_position == 0 and load.end_position == L:
                    w = load.magnitude
                    M_A += w * L ** 2 / 8
                    V_A += 5 * w * L / 8
                    V_B += 3 * w * L / 8

        self._reactions = {
            'left_fixed': {
                'position': 0.0,
                'vertical_reaction': V_A,
                'moment_reaction': -M_A,
            },
            'right_simple': {
                'position': L,
                'vertical_reaction': V_B,
            },
        }

        # 计算内力和变形
        for i, xi in enumerate(self.x):
            V = V_A
            M = V_A * xi - M_A

            for load in self.beam.loads:
                if isinstance(load, PointLoad):
                    if xi > load.position:
                        V -= load.magnitude
                        M -= load.magnitude * (xi - load.position)

                elif isinstance(load, UniformDistributedLoad):
                    if load.start_position == 0 and load.end_position == L:
                        w = load.magnitude
                        V -= w * xi
                        M -= w * xi ** 2 / 2

            self._V[i] = V
            self._M[i] = M

            # 挠度
            v = 0.0
            for load in self.beam.loads:
                if isinstance(load, UniformDistributedLoad):
                    if load.start_position == 0 and load.end_position == L:
                        w = load.magnitude
                        v = w * xi ** 2 * (L - xi) ** 2 * (2 * L - xi) / (48 * EI)

            self._v[i] = v
            self._theta[i] = 0  # 简化处理

    def _solve_numerical(self) -> None:
        """
        数值求解方法
        对于复杂支撑条件使用数值积分
        """
        # 使用有限差分法或数值积分
        # 这里简化处理，使用叠加原理

        L = self.beam.length
        EI = self.beam.get_stiffness()

        # 计算支座反力（平衡方程）
        self._calculate_reactions_equilibrium()

        # 计算内力
        for i, xi in enumerate(self.x):
            V, M = self._calculate_internal_force_equilibrium(xi)
            self._V[i] = V
            self._M[i] = M

        # 计算变形（数值积分）
        # v'' = M / EI
        # 使用有限差分法
        dx = L / (self.num_points - 1)

        # 第一次积分：theta' = M / EI
        for i in range(1, self.num_points):
            self._theta[i] = self._theta[i-1] + self._M[i] * dx / EI

        # 第二次积分：v' = theta
        for i in range(1, self.num_points):
            self._v[i] = self._v[i-1] + self._theta[i] * dx

        # 应用边界条件（简支梁：v=0 at both ends）
        # 修正挠度曲线
        if len(self.beam.supports) >= 2:
            positions = [s.position for s in self.beam.supports]
            if 0 in positions and L in positions:
                # 两端支撑，挠度为零
                # 使用线性修正
                v_correction = -self._v[-1] * self.x / L
                self._v += v_correction

    def _calculate_reactions_equilibrium(self) -> None:
        """
        使用平衡方程计算支座反力
        """
        L = self.beam.length

        # 简支梁处理
        if len(self.beam.supports) == 2:
            # 假设两端简支
            R_A = 0.0  # 左支座反力
            R_B = 0.0  # 右支座反力

            # 平衡方程
            total_load = 0.0
            moment_at_A = 0.0

            for load in self.beam.loads:
                if isinstance(load, PointLoad):
                    total_load += load.magnitude
                    moment_at_A += load.magnitude * load.position

                elif isinstance(load, UniformDistributedLoad):
                    w = load.magnitude
                    a = load.start_position
                    b = load.end_position
                    load_length = b - a
                    eq_pos = a + load_length / 2
                    total_load += w * load_length
                    moment_at_A += w * load_length * eq_pos

            R_B = moment_at_A / L
            R_A = total_load - R_B

            self._reactions = {
                'left': {'position': 0.0, 'reaction': R_A},
                'right': {'position': L, 'reaction': R_B},
            }

    def _calculate_internal_force_equilibrium(self, x: float) -> Tuple[float, float]:
        """
        使用平衡条件计算内力
        """
        V = 0.0
        M = 0.0

        # 加入支座反力的影响
        if 'left' in self._reactions:
            R_A = self._reactions['left']['reaction']
            V = R_A
            M = R_A * x

        # 加入荷载的影响
        for load in self.beam.loads:
            if isinstance(load, PointLoad):
                if x > load.position:
                    V -= load.magnitude
                    M -= load.magnitude * (x - load.position)

            elif isinstance(load, UniformDistributedLoad):
                w = load.magnitude
                a = load.start_position
                b = load.end_position
                if x > a:
                    if x <= b:
                        V -= w * (x - a)
                        M -= w * (x - a) ** 2 / 2
                    else:
                        V -= w * (b - a)
                        M -= w * (b - a) * (x - a - (b - a) / 2)

        return (V, M)

    def _calculate_stresses(self) -> Dict:
        """
        计算应力分布
        """
        # 弯曲应力
        y_top, y_bottom = self.beam.section.get_extreme_fiber_distances()
        I = self.beam.section.get_moment_of_inertia()

        # σ = M × y / I
        # 上边缘应力（负弯矩时为压应力）
        sigma_top = -self._M * y_top / I
        # 下边缘应力
        sigma_bottom = self._M * y_bottom / I

        # 最大弯曲应力（取绝对值较大的）
        sigma_max = np.maximum(np.abs(sigma_top), np.abs(sigma_bottom))

        # 剪应力
        A = self.beam.section.get_area()
        # τ = V / A（简化，实际应该用 τ = VQ/(Ib))
        tau = self._V / A

        # 更精确的剪应力计算
        if hasattr(self.beam.section, 'get_shear_area'):
            shear_area = self.beam.section.get_shear_area()
            tau = self._V / shear_area

        return {
            'position': self.x,
            'bending_stress_top': sigma_top,
            'bending_stress_bottom': sigma_bottom,
            'bending_stress': sigma_max,
            'shear_stress': tau,
        }