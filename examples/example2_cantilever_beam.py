"""
示例2：悬臂梁分析
演示悬臂梁的分析过程
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from beam_toolkit import (
    Beam,
    CircleSection,
    Aluminum,
    PointLoad,
    UniformDistributedLoad,
    FixedSupport,
    FreeEnd,
    BeamVisualizer
)


def main():
    print("=" * 60)
    print("示例2：悬臂梁分析")
    print("=" * 60)
    print()

    # 创建截面（圆形截面：直径0.15m）
    print("创建截面...")
    section = CircleSection(diameter=0.15)
    print(f"  直径: {section.diameter:.3f} m")
    print(f"  面积: {section.get_area():.6f} m^2")
    print(f"  惯性矩: {section.get_moment_of_inertia():.9f} m^4")
    print()

    # 创建材料（铝合金6061-T6）
    print("创建材料...")
    material = Aluminum('6061-T6')
    print(material.info())
    print()

    # 创建悬臂梁（长度2m）
    print("创建悬臂梁...")
    beam = Beam(
        length=2.0,
        section=section,
        material=material,
        name="悬臂梁示例"
    )
    print(f"  梁长度: {beam.length} m")
    print(f"  抗弯刚度 EI: {beam.get_stiffness():.2e} N·m^2")
    print()

    # 添加支撑
    print("添加支撑...")
    beam.add_support(FixedSupport(position=0))  # 左端固定
    beam.add_support(FreeEnd(position=2.0))     # 右端自由
    print(f"  左端: 固定端")
    print(f"  右端: 自由端")
    print()

    # 添加荷载
    print("添加荷载...")
    # 自由端集中力 20kN
    beam.add_load(PointLoad(position=2.0, magnitude=20000))
    print("  自由端集中力: 20kN")
    # 全跨均布荷载 5kN/m
    beam.add_load(UniformDistributedLoad(0, 2.0, 5000))
    print("  均布荷载: 5kN/m")
    print()

    # 求解
    print("求解梁的内力和变形...")
    results = beam.solve()
    print()

    # 显示结果
    print(beam.get_info())
    print()

    # 最大值
    print("=" * 60)
    print("最大值汇总")
    print("=" * 60)
    max_M, pos_M = beam.get_max_bending_moment()
    max_V, pos_V = beam.get_max_shear_force()
    max_v, pos_v = beam.get_max_deflection()

    print(f"  最大弯矩: {max_M/1000:.2f} kN·m @ {pos_M:.2f} m")
    print(f"  最大剪力: {max_V/1000:.2f} kN @ {pos_V:.2f} m")
    print(f"  最大挠度: {max_v*1000:.4f} mm @ {pos_v:.2f} m")
    print(f"  相对挠度: {max_v/beam.length*1000:.4f} /1000L")
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
    visualizer.plot_all(save_path='example2_cantilever_beam.png')

    # 生成报告
    report = visualizer.generate_report('example2_report.txt')
    print("报告已保存至 example2_report.txt")


if __name__ == '__main__':
    main()