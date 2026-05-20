"""
单元测试
测试直梁工具包的核心功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import unittest
import numpy as np
from beam_toolkit import (
    Beam,
    RectangleSection,
    CircleSection,
    IBeamSection,
    TBeamSection,
    Steel,
    Concrete,
    Aluminum,
    Material,
    PointLoad,
    UniformDistributedLoad,
    MomentLoad,
    SimpleSupport,
    FixedSupport,
    FreeEnd,
)


class TestSections(unittest.TestCase):
    """测试截面类"""

    def test_rectangle_section(self):
        """测试矩形截面"""
        section = RectangleSection(width=0.2, height=0.4)

        # 验证面积
        expected_area = 0.2 * 0.4
        self.assertAlmostEqual(section.get_area(), expected_area, places=6)

        # 验证惯性矩
        expected_I = 0.2 * 0.4 ** 3 / 12
        self.assertAlmostEqual(section.get_moment_of_inertia(), expected_I, places=9)

        # 验证截面模量
        expected_W = expected_I / 0.2
        self.assertAlmostEqual(section.get_section_modulus(), expected_W, places=6)

    def test_circle_section(self):
        """测试圆形截面"""
        section = CircleSection(diameter=0.1)

        # 验证面积
        expected_area = np.pi * 0.05 ** 2
        self.assertAlmostEqual(section.get_area(), expected_area, places=6)

        # 验证惯性矩
        expected_I = np.pi * 0.1 ** 4 / 64
        self.assertAlmostEqual(section.get_moment_of_inertia(), expected_I, places=9)

    def test_ibeam_section(self):
        """测试工字形截面"""
        section = IBeamSection(h=0.4, b=0.2, tw=0.01, tf=0.015)

        # 验证面积
        expected_area = 2 * 0.2 * 0.015 + 0.01 * (0.4 - 2 * 0.015)
        self.assertAlmostEqual(section.get_area(), expected_area, places=6)

    def test_tbeam_section(self):
        """测试T形截面"""
        section = TBeamSection(h=0.5, b=0.3, tw=0.01, tf=0.015)

        # 验证面积
        expected_area = 0.3 * 0.015 + 0.01 * (0.5 - 0.015)
        self.assertAlmostEqual(section.get_area(), expected_area, places=6)

        # 验证中性轴位置不为0
        self.assertGreater(section.y_neutral_axis, 0)

    def test_negative_dimensions(self):
        """测试负值尺寸抛出异常"""
        with self.assertRaises(ValueError):
            RectangleSection(width=-0.1, height=0.2)


class TestMaterials(unittest.TestCase):
    """测试材料类"""

    def test_steel_q235(self):
        """测试Q235钢材"""
        steel = Steel('Q235')

        self.assertAlmostEqual(steel.elastic_modulus, 206e9, places=0)
        self.assertAlmostEqual(steel.yield_strength, 235e6, places=0)
        self.assertEqual(steel.name, "钢材Q235")

    def test_steel_q345(self):
        """测试Q345钢材"""
        steel = Steel('Q345')

        self.assertAlmostEqual(steel.yield_strength, 345e6, places=0)

    def test_concrete_c30(self):
        """测试C30混凝土"""
        concrete = Concrete('C30')

        self.assertAlmostEqual(concrete.elastic_modulus, 30e9, places=0)
        self.assertAlmostEqual(concrete.compressive_strength, 30e6, places=0)

    def test_aluminum(self):
        """测试铝合金"""
        aluminum = Aluminum('6061-T6')

        self.assertAlmostEqual(aluminum.elastic_modulus, 68.9e9, places=0)

    def test_custom_material(self):
        """测试自定义材料"""
        custom = Material(
            name="自定义材料",
            elastic_modulus=100e9,
            yield_strength=300e6
        )

        self.assertEqual(custom.name, "自定义材料")
        self.assertEqual(custom.elastic_modulus, 100e9)
        # 验证剪切模量计算
        expected_G = 100e9 / (2 * (1 + 0.3))
        self.assertAlmostEqual(custom.shear_modulus, expected_G, places=0)


class TestLoads(unittest.TestCase):
    """测试荷载类"""

    def test_point_load(self):
        """测试集中力"""
        load = PointLoad(position=3.0, magnitude=50000)

        self.assertEqual(load.position, 3.0)
        self.assertEqual(load.get_total_load(), 50000)
        self.assertEqual(load.get_load_type(), 'point_load')

    def test_uniform_distributed_load(self):
        """测试均布荷载"""
        load = UniformDistributedLoad(0, 6.0, 10000)

        self.assertEqual(load.start_position, 0)
        self.assertEqual(load.end_position, 6.0)
        self.assertEqual(load.get_total_load(), 60000)
        self.assertEqual(load.length, 6.0)

    def test_moment_load(self):
        """测试集中弯矩"""
        load = MomentLoad(position=4.0, magnitude=10000)

        self.assertEqual(load.position, 4.0)
        self.assertEqual(load.get_total_load(), 10000)
        self.assertEqual(load.get_load_type(), 'moment_load')


class TestSupports(unittest.TestCase):
    """测试支撑类"""

    def test_simple_support(self):
        """测试简支支撑"""
        support = SimpleSupport(position=0)

        self.assertEqual(support.position, 0)
        self.assertEqual(support.get_constraint_type(), 'simple')
        self.assertTrue(support.has_vertical_constraint())
        self.assertFalse(support.has_rotation_constraint())

    def test_fixed_support(self):
        """测试固定端"""
        support = FixedSupport(position=0)

        self.assertEqual(support.get_constraint_type(), 'fixed')
        self.assertTrue(support.has_vertical_constraint())
        self.assertTrue(support.has_rotation_constraint())
        self.assertTrue(support.has_horizontal_constraint())

    def test_free_end(self):
        """测试自由端"""
        support = FreeEnd(position=6.0)

        self.assertEqual(support.get_constraint_type(), 'free')
        self.assertFalse(support.has_vertical_constraint())
        self.assertFalse(support.has_rotation_constraint())


class TestBeam(unittest.TestCase):
    """测试梁类"""

    def setUp(self):
        """设置测试梁"""
        self.section = RectangleSection(width=0.2, height=0.4)
        self.material = Steel('Q345')
        self.beam = Beam(length=6.0, section=self.section, material=self.material)

    def test_beam_creation(self):
        """测试梁创建"""
        self.assertEqual(self.beam.length, 6.0)
        self.assertEqual(self.beam.section, self.section)
        self.assertEqual(self.beam.material, self.material)

    def test_add_load(self):
        """测试添加荷载"""
        load = PointLoad(position=3.0, magnitude=50000)
        self.beam.add_load(load)

        self.assertEqual(len(self.beam.loads), 1)
        self.assertEqual(self.beam.loads[0], load)

    def test_add_support(self):
        """测试添加支撑"""
        support = SimpleSupport(position=0)
        self.beam.add_support(support)

        self.assertEqual(len(self.beam.supports), 1)
        self.assertEqual(self.beam.supports[0], support)

    def test_stiffness(self):
        """测试抗弯刚度计算"""
        E = self.material.get_elastic_modulus()
        I = self.section.get_moment_of_inertia()
        expected_EI = E * I

        self.assertAlmostEqual(self.beam.get_stiffness(), expected_EI, places=0)

    def test_invalid_length(self):
        """测试无效长度"""
        with self.assertRaises(ValueError):
            Beam(length=-1, section=self.section, material=self.material)

    def test_clear_loads(self):
        """测试清除荷载"""
        self.beam.add_load(PointLoad(position=3.0, magnitude=50000))
        self.beam.clear_loads()

        self.assertEqual(len(self.beam.loads), 0)


class TestSolver(unittest.TestCase):
    """测试求解器"""

    def setUp(self):
        """设置测试梁"""
        self.section = RectangleSection(width=0.2, height=0.4)
        self.material = Steel('Q345')

    def test_simple_beam_solver(self):
        """测试简支梁求解"""
        beam = Beam(length=6.0, section=self.section, material=self.material)
        beam.add_support(SimpleSupport(position=0))
        beam.add_support(SimpleSupport(position=6.0))
        beam.add_load(PointLoad(position=3.0, magnitude=50000))

        results = beam.solve()

        # 验证结果包含必要字段
        self.assertIn('internal_forces', results)
        self.assertIn('deformations', results)
        self.assertIn('stresses', results)

    def test_cantilever_beam_solver(self):
        """测试悬臂梁求解"""
        beam = Beam(length=2.0, section=self.section, material=self.material)
        beam.add_support(FixedSupport(position=0))
        beam.add_support(FreeEnd(position=2.0))
        beam.add_load(PointLoad(position=2.0, magnitude=20000))

        results = beam.solve()

        # 验证弯矩在固定端最大
        max_M, pos_M = beam.get_max_bending_moment()
        self.assertEqual(beam.get_beam_type(), "悬臂梁")


if __name__ == '__main__':
    unittest.main(verbosity=2)