"""
直梁面向对象解工具包 - 主程序入口
演示工具包的核心功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    LinearDistributedLoad,
    MomentLoad,
    SimpleSupport,
    FixedSupport,
    FreeEnd,
    BeamVisualizer,
)


def demo_simple_beam():
    """
    示例：简支梁分析
    """
    print("\n" + "=" * 60)
    print("示例：简支梁分析")
    print("=" * 60)

    # 创建截面和材料
    section = RectangleSection(width=0.3, height=0.5)
    material = Steel('Q345')

    # 创建梁
    beam = Beam(
        length=6.0,
        section=section,
        material=material,
        name="简支梁示例"
    )

    # 添加支撑
    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=6.0))

    # 添加荷载
    beam.add_load(PointLoad(position=3.0, magnitude=50000))
    beam.add_load(UniformDistributedLoad(0, 6.0, 10000))

    # 求解
    beam.solve()

    # 显示结果
    print(beam.get_info())

    # 安全性检查
    safety = beam.check_safety()
    print(f"\n安全状态: {'安全 ✓' if safety['is_safe'] else '不安全 ✗'}")
    print(f"安全系数: {safety['bending_safety_factor']:.2f}")

    return beam


def demo_cantilever_beam():
    """
    示例：悬臂梁分析
    """
    print("\n" + "=" * 60)
    print("示例：悬臂梁分析")
    print("=" * 60)

    # 创建圆形截面和铝合金材料
    section = CircleSection(diameter=0.1)
    material = Aluminum('6061-T6')

    # 创建悬臂梁
    beam = Beam(
        length=2.0,
        section=section,
        material=material,
        name="悬臂梁示例"
    )

    # 添加支撑
    beam.add_support(FixedSupport(position=0))
    beam.add_support(FreeEnd(position=2.0))

    # 添加荷载
    beam.add_load(PointLoad(position=2.0, magnitude=20000))
    beam.add_load(UniformDistributedLoad(0, 2.0, 5000))

    # 求解
    beam.solve()

    # 显示结果
    print(beam.get_info())

    return beam


def demo_ibeam():
    """
    示例：工字形截面梁
    """
    print("\n" + "=" * 60)
    print("示例：工字形截面梁")
    print("=" * 60)

    # 创建工字形截面
    section = IBeamSection(
        h=0.400, b=0.200, tw=0.008, tf=0.013,
        name="HN400×200"
    )

    print(f"截面面积: {section.get_area()*1e6:.0f} mm²")
    print(f"惯性矩(Iz): {section.get_moment_of_inertia('z')*1e12:.0f} mm⁴")

    # 创建材料
    material = Steel('Q420')

    # 创建梁
    beam = Beam(
        length=8.0,
        section=section,
        material=material,
        name="工字形截面梁"
    )

    # 添加支撑和荷载
    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=8.0))
    beam.add_load(PointLoad(position=4.0, magnitude=100000))
    beam.add_load(UniformDistributedLoad(0, 8.0, 20000))

    # 求解
    beam.solve()

    # 显示结果
    print(beam.get_info())

    return beam


def main():
    """
    主函数
    """
    print("=" * 60)
    print("直梁面向对象解工具包")
    print("Beam Object-Oriented Analysis Toolkit")
    print("=" * 60)
    print()
    print("功能概览：")
    print("  - 多种截面类型：矩形、圆形、工字形、T形")
    print("  - 材料库：钢材、混凝土、铝合金")
    print("  - 荷载类型：集中力、均布荷载、线性分布荷载、弯矩")
    print("  - 边界条件：固定端、简支、悬臂、铰支撑")
    print("  - 计算功能：内力、应力、变形分析")
    print("  - 可视化：弯矩图、剪力图、挠度图")
    print("  - 安全性检查：应力验算、挠度限值")
    print()

    # 运行示例
    beam1 = demo_simple_beam()
    beam2 = demo_cantilever_beam()
    beam3 = demo_ibeam()

    print("\n" + "=" * 60)
    print("工具包演示完成")
    print("=" * 60)
    print()
    print("如需运行详细示例，请查看 examples 目录中的示例文件")
    print("如需可视化输出，请运行带绘图的示例程序")


if __name__ == '__main__':
    main()