"""
示例1：简支梁分析
演示简支梁在集中力和均布荷载作用下的分析
"""

from beam_toolkit import (
    Beam,
    RectangleSection,
    Steel,
    PointLoad,
    UniformDistributedLoad,
    SimpleSupport,
    BeamVisualizer
)


def main():
    print("=" * 60)
    print("示例1：简支梁分析")
    print("=" * 60)
    print()

    # 创建截面（矩形截面：宽0.3m，高0.5m）
    print("创建截面...")
    section = RectangleSection(width=0.3, height=0.5)
    print(f"  截面面积: {section.get_area():.6f} m²")
    print(f"  惯性矩: {section.get_moment_of_inertia():.9f} m⁴")
    print(f"  截面模量: {section.get_section_modulus():.6f} m³")
    print()

    # 创建材料（Q345钢材）
    print("创建材料...")
    material = Steel('Q345')
    print(material.info())
    print()

    # 创建梁（长度6m）
    print("创建梁...")
    beam = Beam(
        length=6.0,
        section=section,
        material=material,
        name="简支梁示例"
    )
    print(f"  梁长度: {beam.length} m")
    print(f"  抗弯刚度 EI: {beam.get_stiffness():.2e} N·m²")
    print()

    # 添加支撑（两端简支）
    print("添加支撑...")
    beam.add_support(SimpleSupport(position=0))   # 左端简支
    beam.add_support(SimpleSupport(position=6.0))  # 右端简支
    print(f"  支撑数量: {len(beam.supports)}")
    print()

    # 添加荷载
    print("添加荷载...")
    # 中点集中力 50kN
    beam.add_load(PointLoad(position=3.0, magnitude=50000))
    print("  集中力: 50kN @ 3.0m")
    # 全跨均布荷载 10kN/m
    beam.add_load(UniformDistributedLoad(0, 6.0, 10000))
    print("  均布荷载: 10kN/m @ 0-6m")
    print()

    # 求解
    print("求解梁的内力和变形...")
    results = beam.solve()
    print()

    # 显示结果
    print(beam.get_info())
    print()

    # 安全性检查
    print("=" * 60)
    print("安全性检查")
    print("=" * 60)
    safety = beam.check_safety()
    print(f"  最大弯曲应力: {safety['max_bending_stress']/1e6:.2f} MPa")
    print(f"  许用应力: {safety['allowable_stress']/1e6:.2f} MPa")
    print(f"  安全系数: {safety['bending_safety_factor']:.2f}")
    print(f"  安全状态: {'安全 ✓' if safety['is_safe'] else '不安全 ✗'}")
    print()

    # 可视化
    print("绘制图形...")
    visualizer = BeamVisualizer(beam)
    visualizer.plot_all(save_path='example1_simple_beam.png')

    # 生成报告
    report = visualizer.generate_report('example1_report.txt')
    print("报告已保存至 example1_report.txt")


if __name__ == '__main__':
    main()