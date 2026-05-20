"""
示例5：自定义材料创建
演示如何创建自定义材料
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from beam_toolkit import (
    Beam,
    RectangleSection,
    Material,
    PointLoad,
    SimpleSupport,
    BeamVisualizer
)


def main():
    print("=" * 60)
    print("示例5：自定义材料创建")
    print("=" * 60)
    print()

    # 创建自定义材料
    print("创建自定义材料...")
    custom_material = Material(
        name="自定义铝合金",
        elastic_modulus=70e9,         # 弹性模量 70 GPa
        yield_strength=280e6,         # 屈服强度 280 MPa
        ultimate_strength=350e6,      # 极限强度 350 MPa
        density=2700,                  # 密度 2700 kg/m^3
        poisson_ratio=0.33,           # 泊松比 0.33
        thermal_expansion=23e-6,       # 热膨胀系数 23×10⁻⁶/°C
        allowable_stress=180e6        # 许用应力 180 MPa
    )
    print(custom_material.info())
    print()

    # 使用自定义材料创建梁
    print("创建梁...")
    section = RectangleSection(width=0.15, height=0.25)
    beam = Beam(
        length=3.0,
        section=section,
        material=custom_material,
        name="自定义材料梁"
    )
    print(f"  梁长度: {beam.length} m")
    print(f"  截面: {section.width*1000:.0f}×{section.height*1000:.0f} mm")
    print()

    # 添加支撑
    print("添加支撑...")
    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=3.0))
    print()

    # 添加荷载
    print("添加荷载...")
    beam.add_load(PointLoad(position=1.5, magnitude=25000))
    print("  集中力: 25kN @ 1.5m")
    print()

    # 求解
    print("求解...")
    results = beam.solve()
    print()

    # 显示结果
    print(beam.get_info())
    print()

    # 计算梁的质量
    try:
        mass = beam.get_mass()
        print(f"梁的质量: {mass:.2f} kg")
    except ValueError as e:
        print(f"无法计算质量: {e}")
    print()

    # 安全性检查
    print("=" * 60)
    print("安全性检查")
    print("=" * 60)
    safety = beam.check_safety()
    print(f"  最大弯曲应力: {safety['max_bending_stress']/1e6:.2f} MPa")
    print(f"  许用应力: {safety['allowable_stress']/1e6:.2f} MPa")
    print(f"  安全系数: {safety['bending_safety_factor']:.2f}")
    print(f"  安全状态: {'安全 [OK]' if safety['is_safe'] else '不安全 [FAIL]'}")
    print()

    # 可视化
    print("绘制图形...")
    visualizer = BeamVisualizer(beam)
    visualizer.plot_all(save_path='example5_custom_material.png')


if __name__ == '__main__':
    main()