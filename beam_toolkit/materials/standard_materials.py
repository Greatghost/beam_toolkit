"""
标准材料类
预定义常用工程材料
"""

from .material import Material


class Steel(Material):
    """
    钢材材料类

    提供常用钢材的预定义参数
    """

    # 预定义钢材类型
    TYPES = {
        'Q235': {
            'E': 206e9,  # 206 GPa
            'sigma_y': 235e6,  # 235 MPa
            'sigma_u': 375e6,  # 375 MPa
            'rho': 7850,  # 7850 kg/m^3
            'poisson': 0.3,
            'alpha': 12e-6,  # 12×10⁻⁶ /°C
        },
        'Q345': {
            'E': 206e9,
            'sigma_y': 345e6,
            'sigma_u': 470e6,
            'rho': 7850,
            'poisson': 0.3,
            'alpha': 12e-6,
        },
        'Q420': {
            'E': 206e9,
            'sigma_y': 420e6,
            'sigma_u': 520e6,
            'rho': 7850,
            'poisson': 0.3,
            'alpha': 12e-6,
        },
        'A36': {
            'E': 200e9,
            'sigma_y': 250e6,
            'sigma_u': 400e6,
            'rho': 7850,
            'poisson': 0.3,
            'alpha': 11.7e-6,
        },
        'SS304': {
            'E': 193e9,
            'sigma_y': 205e6,
            'sigma_u': 515e6,
            'rho': 8000,
            'poisson': 0.3,
            'alpha': 17.2e-6,
        },
    }

    def __init__(self, steel_type: str = 'Q235', safety_factor: float = 1.5):
        """
        初始化钢材

        Args:
            steel_type: 钢材类型（'Q235', 'Q345', 'Q420', 'A36', 'SS304'）
            safety_factor: 安全系数
        """
        if steel_type not in self.TYPES:
            raise ValueError(f"不支持的钢材类型: {steel_type}。可用类型: {list(self.TYPES.keys())}")

        params = self.TYPES[steel_type]
        allowable = params['sigma_y'] / safety_factor

        super().__init__(
            name=f"钢材{steel_type}",
            elastic_modulus=params['E'],
            yield_strength=params['sigma_y'],
            ultimate_strength=params['sigma_u'],
            density=params['rho'],
            poisson_ratio=params['poisson'],
            thermal_expansion=params['alpha'],
            allowable_stress=allowable,
        )

        self.steel_type = steel_type
        self.safety_factor = safety_factor


class Concrete(Material):
    """
    混凝土材料类

    提供常用混凝土的预定义参数
    """

    # 预定义混凝土类型
    TYPES = {
        'C25': {
            'E': 28e9,  # 28 GPa
            'sigma_c': 25e6,  # 25 MPa (抗压强度)
            'sigma_t': 1.78e6,  # 抗拉强度
            'rho': 2400,
            'poisson': 0.2,
        },
        'C30': {
            'E': 30e9,
            'sigma_c': 30e6,
            'sigma_t': 2.01e6,
            'rho': 2400,
            'poisson': 0.2,
        },
        'C35': {
            'E': 31.5e9,
            'sigma_c': 35e6,
            'sigma_t': 2.2e6,
            'rho': 2400,
            'poisson': 0.2,
        },
        'C40': {
            'E': 32.5e9,
            'sigma_c': 40e6,
            'sigma_t': 2.39e6,
            'rho': 2400,
            'poisson': 0.2,
        },
        'C50': {
            'E': 34.5e9,
            'sigma_c': 50e6,
            'sigma_t': 2.64e6,
            'rho': 2400,
            'poisson': 0.2,
        },
    }

    def __init__(self, concrete_type: str = 'C30', safety_factor: float = 1.4):
        """
        初始化混凝土

        Args:
            concrete_type: 混凝土类型（'C25', 'C30', 'C35', 'C40', 'C50'）
            safety_factor: 安全系数
        """
        if concrete_type not in self.TYPES:
            raise ValueError(f"不支持的混凝土类型: {concrete_type}。可用类型: {list(self.TYPES.keys())}")

        params = self.TYPES[concrete_type]
        allowable_compressive = params['sigma_c'] / safety_factor

        super().__init__(
            name=f"混凝土{concrete_type}",
            elastic_modulus=params['E'],
            ultimate_strength=params['sigma_c'],
            density=params['rho'],
            poisson_ratio=params['poisson'],
            allowable_stress=allowable_compressive,
        )

        self.concrete_type = concrete_type
        self.compressive_strength = params['sigma_c']
        self.tensile_strength = params['sigma_t']
        self.safety_factor = safety_factor


class Aluminum(Material):
    """
    铝合金材料类

    提供常用铝合金的预定义参数
    """

    # 预定义铝合金类型
    TYPES = {
        '6061-T6': {
            'E': 68.9e9,  # 68.9 GPa
            'sigma_y': 276e6,  # 276 MPa
            'sigma_u': 310e6,  # 310 MPa
            'rho': 2700,
            'poisson': 0.33,
            'alpha': 23.6e-6,
        },
        '7075-T6': {
            'E': 71.7e9,
            'sigma_y': 503e6,
            'sigma_u': 572e6,
            'rho': 2810,
            'poisson': 0.33,
            'alpha': 23.4e-6,
        },
        '2024-T4': {
            'E': 73.1e9,
            'sigma_y': 324e6,
            'sigma_u': 469e6,
            'rho': 2770,
            'poisson': 0.33,
            'alpha': 23.2e-6,
        },
    }

    def __init__(self, aluminum_type: str = '6061-T6', safety_factor: float = 1.5):
        """
        初始化铝合金

        Args:
            aluminum_type: 铝合金类型（'6061-T6', '7075-T6', '2024-T4'）
            safety_factor: 安全系数
        """
        if aluminum_type not in self.TYPES:
            raise ValueError(f"不支持的铝合金类型: {aluminum_type}。可用类型: {list(self.TYPES.keys())}")

        params = self.TYPES[aluminum_type]
        allowable = params['sigma_y'] / safety_factor

        super().__init__(
            name=f"铝合金{aluminum_type}",
            elastic_modulus=params['E'],
            yield_strength=params['sigma_y'],
            ultimate_strength=params['sigma_u'],
            density=params['rho'],
            poisson_ratio=params['poisson'],
            thermal_expansion=params['alpha'],
            allowable_stress=allowable,
        )

        self.aluminum_type = aluminum_type
        self.safety_factor = safety_factor