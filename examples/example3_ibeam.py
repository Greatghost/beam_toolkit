"""
示例3：工字形截面梁分析
演示工字形截面（H型钢）梁的分析
"""

from beam_toolkit import (
    Beam,
    IBeamSection,
    TBeamSection,
    Steel,
    PointLoad,
    UniformDistributedLoad,
    SimpleSupport,
    BeamVisualizer
)


def main():
    print("=" * 60)
    print("示例3：工字形截面梁分析")
    print("=" * 60)
    print()

    # 创建工字形截面（类似H型钢HN400×200）
    # 参数：h=400mm, b=200mm, tw=8mm, tf=13mm
    print("创建工字形截面...")
    section = IBeamSection(
        h=0.400,    # 总高度 400mm
        b=0.200,    # 翼缘宽度 200mm
        tw=0.008,   # 腹板厚度 8mm
        tf=0.013,   # 翼缘厚度 13mm
        name="HN400×200"
    )

    print(f"  截面尺寸:")
    print(f"    h = {section.h*1000:.0f} mm")
    print(f"    b = {section.b*1000:.0f} mm")
    print(f"    tw = {section.tw*1000:.0f} mm")
    print(f"    tf = {section.tf*1000:.0f} mm")
    print(f"  截面面积: {section.get_area()*1e6:.0f} mm²")
    print(f"  惯性矩(Iz): {section.get_moment_of_inertia('z')*1e12:.0f} mm⁴")
    print(f"  惯性矩(Iy): {section.get_moment_of_inertia('y')*1e12:.0f} mm⁴")
    print(f"  强轴截面模量: {section.get_section_modulus('z')*1e9:.0f} mm³")
    print()

    # 创建材料（Q420钢材）
    print("创建材料...")
    material = Steel('Q420')
    print(material.info())
    print()

    # 创建梁（长度8m）
    print("创建梁...")
    beam = Beam(
        length=8.0,
        section=section,
        material=material,
        name="工字形截面梁"
    )
    print(f"  梁长度: {beam.length} m")
    print(f"  抗弯刚度 EI: {beam.get_stiffness():.2e} N·m²")
    print()

    # 添加支撑（两端简支）
    print("添加支撑...")
    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=8.0))
    print()

    # 添加荷载
    print("添加荷载...")
    # 中点集中力 100kN
    beam.add_load(PointLoad(position=4.0, magnitude=100000))
    print("  集中力: 100kN @ 4.0m")
    # 全跨均布荷载 20kN/m（模拟楼板荷载）
    beam.add_load(UniformDistributedLoad(0, 8.0, 20000))
    print("  均布荷载: 20kN/m")
    print()

    # 求解
    print("求解梁的内力和变形...")
    results = beam.solve()
    print()

    # 显示结果
    print(beam.get_info())
    print()

    # 可视化
    print("绘制图形...")
    visualizer = BeamVisualizer(beam)
    visualizer.plot_all(save_path='example3_ibeam.png')

    # 绘制应力图
    visualizer.plot_stress(save_path='example3_stress.png')

    # 安全性检查
    print("=" * 60)
    print("安全性检查")
    print("=" * 60)
    safety = beam.check_safety()
    print(f"  最大弯曲应力: {safety['max_bending_stress']/1e6:.2f} MPa")
    print(f"  许用应力: {safety['allowable_stress']/1e6:.2f} MPa")
    print(f"  安全系数: {safety['bending_safety_factor']:.2f}")
    print(f"  最大挠度: {safety['max_deflection']*1000:.4f} mm")
    print(f"  挠度限值: {safety['deflection_limit']*1000:.2f} mm (L/250)")
    print(f"  挠度检查: {'满足 ✓' if safety['deflection_safe'] else '不满足 ✗'}")
    print()

    # 生成报告
    report = visualizer.generate_report('example3_report.txt')
    print("报告已保存至 example3_report.txt")

    # 演示T形截面
    print()
    print("=" * 60)
    print("T形截面示例")
    print("=" * 60)
    t_section = TBeamSection(
        h=0.500,    # 总高度 500mm
        b=0.300,    # 翼缘宽度 300mm
        tw=0.010,   # 腹板厚度 10mm
        tf=0.015,   # 翼缘厚度 15mm
        name="T形截面"
    )
    print(f"  截面面积: {t_section.get_area()*1e6:.0f} mm²")
    print(f"  惯性矩: {t_section.get_moment_of_inertia()*1e12:.0f} mm⁴")
    print(f"  中性轴位置: {t_section.y_neutral_axis*1000:.1f} mm（从底部起）")
    print(f"  上边缘截面模量: {t_section.get_section_modulus_top()*1e9:.0f} mm³")
    print(f"  下边缘截面模量: {t_section.get_section_modulus_bottom()*1e9:.0f} mm³")


if __name__ == '__main__':
    main()