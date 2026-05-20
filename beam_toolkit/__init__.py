"""
直梁面向对象解工具包
一个用于直梁力学分析的产品级工具包
"""

__version__ = "1.0.0"
__author__ = "Beam Toolkit Team"

from .core.beam import Beam
from .sections.base import Section
from .sections.rectangle import RectangleSection
from .sections.circle import CircleSection
from .sections.ibeam import IBeamSection
from .sections.tbeam import TBeamSection
from .materials.material import Material
from .materials.standard_materials import Steel, Concrete, Aluminum
from .loads.base import Load
from .loads.point_load import PointLoad
from .loads.distributed_load import DistributedLoad, UniformDistributedLoad, LinearDistributedLoad
from .loads.moment_load import MomentLoad
from .supports.base import Support
from .supports.fixed_support import FixedSupport
from .supports.simple_support import SimpleSupport
from .supports.free_end import FreeEnd
from .solvers.analytical_solver import AnalyticalSolver
from .visualization.plotter import BeamVisualizer

__all__ = [
    'Beam',
    'Section', 'RectangleSection', 'CircleSection', 'IBeamSection', 'TBeamSection',
    'Material', 'Steel', 'Concrete', 'Aluminum',
    'Load', 'PointLoad', 'DistributedLoad', 'UniformDistributedLoad', 'LinearDistributedLoad', 'MomentLoad',
    'Support', 'FixedSupport', 'SimpleSupport', 'FreeEnd',
    'AnalyticalSolver',
    'BeamVisualizer',
]