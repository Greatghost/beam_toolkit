"""
示例4：多种荷载组合分析
演示梁在多种荷载组合作用下的分析
"""

from beam_toolkit import (
    Beam,
    RectangleSection,
    Concrete,
    PointLoad,
    UniformDistributedLoad,
    LinearDistributedLoad,
    MomentLoad,
    SimpleSupport,
    FixedSupport,
    BeamVisualizer
)


def main():
    print("=" * 60)
    print("示例4：多种荷载组合分析")
    print("=" * 60)
    print()

    # 创建截面
    print("创建截面...")
    section = RectangleSection(width=0.25, height=0.50)
    print(f"  矩形截面: {section.width*1000:.0f}×{section.height*1000:.0f} mm")
    print()

    # 创建材料（混凝土C40）
    print("创建材料...")
    material = Concrete('C40')
    print(material.info())
    print()

    # 创建梁（长度5m）
    print("创建梁...")
    beam = Beam(
        length=5.0,
        section=section,
        material=material,
        name="多种荷载组合梁"
    )
    print(f"  梁长度: {beam.length} m")
    print()

    # 添加支撑（两端简支）
    print("添加支撑...")
    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=5.0))
    print()

    # 添加多种荷载
    print("添加荷载...")
    print("  1. 集中力 30kN @ 1.0m")
    beam.add_load(PointLoad(position=1.0, magnitude=30000))

    print("  2. 集中力 20kN @ 3.5m")
    beam.add_load(PointLoad(position=3.5, magnitude=20000))

    print("  3. 均布荷载 8kN/m @ 0-2m")
    beam.add_load(UniformDistributedLoad(0, 2.0, 8000))

    print("  4. 线性分布荷载 5-15kN/m @ 2-4m")
    beam.add_load(LinearDistributedLoad(2.0, 4.0, 5000, 15000))

    print("  5. 集中弯矩 10kN·m @ 4.5m")
    beam.add_load(MomentLoad(position=4.5, magnitude=10000))
    print()

    # 求解
    print("求解梁的内力和变形...")
    results = beam.solve()
    print()

    # 显示结果
    print(beam.get_info())
    print()

    # 显示荷载详情
    print("=" * 60)
    print("荷载详情")
    print("=" * 60)
    for i, load in enumerate(beam.loads, 1):
        print(f"  {i}. {load}")
    print()

    # 最大值汇总
    print("=" * 60)
    print("最大值汇总")
    print("=" * 60)
    max_M, pos_M = beam.get_max_bending_moment()
    max_V, pos_V = beam.get_max_shear_force()
    max_v, pos_v = beam.get_max_deflection()

    print(f"  最大弯矩: {max_M/1000:.2f} kN·m @ {pos_M:.2f} m")
    print(f"  最大剪力: {max_V/1000:.2f} kN @ {pos_V:.2f} m")
    print(f"  最大挠度: {max_v*1000:.4f} mm @ {pos_v:.2f} m")
    print()

    # 安全性检查
    print("=" * 60)
    print("安全性检查")
    print("=" * 60)
    safety = beam.check_safety()
    print(f"  最大弯曲应力: {safety['max_bending_stress']/1e6:.2f} MPa")
    print(f"  许用应力: {safety['allowable_stress']/1e6:.2f} MPa (混凝土抗压强度/{safety['bending_safety_factor']})")
    print(f"  安全状态: {'安全 ✓' if safety['is_safe'] else '不安全 ✗'}")
    print()

    # 可视化
    print("绘制图形...")
    visualizer = BeamVisualizer(beam)
    visualizer.plot_all(save_path='example4_combined_loads.png')

    # 生成报告
    report = visualizer.generate_report('example4_report.txt')
    print("报告已保存至 example4_report.txt")


if __name__ == '__main__':
    main()