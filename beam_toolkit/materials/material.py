"""
材料基类
定义材料的基本属性
"""

from abc import ABC
from typing import Optional


class Material(ABC):
    """
    材料基类

    所有材料类型必须继承此类
    """

    def __init__(
        self,
        name: str,
        elastic_modulus: float,  # 弹性模量 E (Pa)
        yield_strength: Optional[float] = None,  # 屈服强度 (Pa)
        ultimate_strength: Optional[float] = None,  # 极限强度 (Pa)
        density: Optional[float] = None,  # 密度 (kg/m^3)
        poisson_ratio: float = 0.3,  # 泊松比
        shear_modulus: Optional[float] = None,  # 剪切模量 G (Pa)
        thermal_expansion: Optional[float] = None,  # 热膨胀系数 (1/°C)
        allowable_stress: Optional[float] = None,  # 许用应力 (Pa)
    ):
        """
        初始化材料

        Args:
            name: 材料名称
            elastic_modulus: 弹性模量 E (Pa)
            yield_strength: 屈服强度 (Pa)
            ultimate_strength: 极限强度 (Pa)
            density: 密度 (kg/m^3)
            poisson_ratio: 泊松比（默认0.3）
            shear_modulus: 剪切模量 G (Pa)，如果不提供则由 E 和 poisson 计算
            thermal_expansion: 热膨胀系数 (1/°C)
            allowable_stress: 许用应力 (Pa)
        """
        if elastic_modulus <= 0:
            raise ValueError("弹性模量必须为正值")

        self.name = name
        self.elastic_modulus = elastic_modulus
        self.yield_strength = yield_strength
        self.ultimate_strength = ultimate_strength
        self.density = density
        self.poisson_ratio = poisson_ratio
        self.thermal_expansion = thermal_expansion
        self.allowable_stress = allowable_stress

        # 剪切模量 G = E / (2(1+poisson))
        if shear_modulus is not None:
            self.shear_modulus = shear_modulus
        else:
            self.shear_modulus = elastic_modulus / (2 * (1 + poisson_ratio))

    def get_elastic_modulus(self) -> float:
        """
        获取弹性模量

        Returns:
            弹性模量 E (Pa)
        """
        return self.elastic_modulus

    def get_shear_modulus(self) -> float:
        """
        获取剪切模量

        Returns:
            剪切模量 G (Pa)
        """
        return self.shear_modulus

    def get_yield_strength(self) -> Optional[float]:
        """
        获取屈服强度

        Returns:
            屈服强度 (Pa)，如果未定义返回None
        """
        return self.yield_strength

    def get_ultimate_strength(self) -> Optional[float]:
        """
        获取极限强度

        Returns:
            极限强度 (Pa)，如果未定义返回None
        """
        return self.ultimate_strength

    def get_allowable_stress(self, safety_factor: float = 1.5) -> float:
        """
        获取许用应力

        Args:
            safety_factor: 安全系数（如果未定义allowable_stress时使用）

        Returns:
            许用应力 (Pa)
        """
        if self.allowable_stress is not None:
            return self.allowable_stress

        if self.yield_strength is not None:
            return self.yield_strength / safety_factor

        if self.ultimate_strength is not None:
            return self.ultimate_strength / (safety_factor * 1.5)

        raise ValueError("材料未定义强度参数，无法计算许用应力")

    def get_density(self) -> Optional[float]:
        """
        获取密度

        Returns:
            密度 (kg/m^3)，如果未定义返回None
        """
        return self.density

    def get_poisson_ratio(self) -> float:
        """
        获取泊松比

        Returns:
            泊松比
        """
        return self.poisson_ratio

    def get_thermal_expansion(self) -> Optional[float]:
        """
        获取热膨胀系数

        Returns:
            热膨胀系数 (1/°C)，如果未定义返回None
        """
        return self.thermal_expansion

    def __repr__(self) -> str:
        return f"Material({self.name}, E={self.elastic_modulus/1e9:.1f}GPa)"

    def __str__(self) -> str:
        return f"{self.name}: E={self.elastic_modulus/1e9:.2f}GPa"

    def info(self) -> str:
        """
        获取材料详细信息

        Returns:
            材料详细信息字符串
        """
        info_lines = [f"材料: {self.name}"]
        info_lines.append(f"  弹性模量 E = {self.elastic_modulus/1e9:.2f} GPa")
        info_lines.append(f"  剪切模量 G = {self.shear_modulus/1e9:.2f} GPa")
        info_lines.append(f"  泊松比 poisson = {self.poisson_ratio:.3f}")

        if self.yield_strength:
            info_lines.append(f"  屈服强度 sigma_y = {self.yield_strength/1e6:.1f} MPa")
        if self.ultimate_strength:
            info_lines.append(f"  极限强度 sigma_u = {self.ultimate_strength/1e6:.1f} MPa")
        if self.density:
            info_lines.append(f"  密度 rho = {self.density:.0f} kg/m^3")
        if self.thermal_expansion:
            info_lines.append(f"  热膨胀系数 alpha = {self.thermal_expansion:.2e} /°C")

        return '\n'.join(info_lines)