"""
直梁面向对象解工具包 - 简化演示
演示工具包的核心功能（避免编码问题）
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
    Steel,
    Aluminum,
    PointLoad,
    UniformDistributedLoad,
    SimpleSupport,
    FixedSupport,
    FreeEnd,
)


def demo_simple_beam():
    """
    Demo: Simple Beam Analysis
    """
    print("\n" + "=" * 60)
    print("Demo 1: Simple Beam Analysis")
    print("=" * 60)

    # Create section and material
    section = RectangleSection(width=0.3, height=0.5)
    print("Section: Rectangle 0.3m x 0.5m")
    print(f"  Area: {section.get_area():.6f} m^2")
    print(f"  Moment of Inertia: {section.get_moment_of_inertia():.9f} m^4")

    material = Steel('Q345')
    print(f"Material: Steel Q345")
    print(f"  Elastic Modulus: {material.elastic_modulus/1e9:.1f} GPa")

    # Create beam
    beam = Beam(
        length=6.0,
        section=section,
        material=material,
        name="Simple Beam Demo"
    )

    # Add supports
    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=6.0))

    # Add loads
    beam.add_load(PointLoad(position=3.0, magnitude=50000))
    beam.add_load(UniformDistributedLoad(0, 6.0, 10000))
    print(f"Loads:")
    print(f"  Point Load: 50kN at 3.0m")
    print(f"  UDL: 10kN/m over 0-6m")

    # Solve
    beam.solve()

    # Results
    max_M, pos_M = beam.get_max_bending_moment()
    max_V, pos_V = beam.get_max_shear_force()
    max_v, pos_v = beam.get_max_deflection()

    print(f"\nResults:")
    print(f"  Beam Type: {beam.get_beam_type()}")
    print(f"  Max Moment: {max_M/1000:.2f} kN*m at {pos_M:.2f} m")
    print(f"  Max Shear: {max_V/1000:.2f} kN at {pos_V:.2f} m")
    print(f"  Max Deflection: {max_v*1000:.4f} mm at {pos_v:.2f} m")

    # Safety check
    safety = beam.check_safety()
    print(f"\nSafety Check:")
    print(f"  Max Bending Stress: {safety['max_bending_stress']/1e6:.2f} MPa")
    print(f"  Allowable Stress: {safety['allowable_stress']/1e6:.2f} MPa")
    print(f"  Safety Factor: {safety['bending_safety_factor']:.2f}")
    print(f"  Status: {'SAFE' if safety['is_safe'] else 'NOT SAFE'}")

    return beam


def demo_cantilever_beam():
    """
    Demo: Cantilever Beam Analysis
    """
    print("\n" + "=" * 60)
    print("Demo 2: Cantilever Beam Analysis")
    print("=" * 60)

    # Create circular section and aluminum material
    section = CircleSection(diameter=0.1)
    print(f"Section: Circle d=0.1m")
    print(f"  Area: {section.get_area():.6f} m^2")

    material = Aluminum('6061-T6')
    print(f"Material: Aluminum 6061-T6")
    print(f"  Elastic Modulus: {material.elastic_modulus/1e9:.1f} GPa")

    # Create cantilever beam
    beam = Beam(
        length=2.0,
        section=section,
        material=material,
        name="Cantilever Beam Demo"
    )

    # Add supports
    beam.add_support(FixedSupport(position=0))
    beam.add_support(FreeEnd(position=2.0))
    print(f"Supports: Fixed at 0m, Free at 2m")

    # Add loads
    beam.add_load(PointLoad(position=2.0, magnitude=20000))
    beam.add_load(UniformDistributedLoad(0, 2.0, 5000))
    print(f"Loads:")
    print(f"  Point Load: 20kN at free end")
    print(f"  UDL: 5kN/m")

    # Solve
    beam.solve()

    # Results
    print(f"\nResults:")
    print(f"  Beam Type: {beam.get_beam_type()}")
    max_M, pos_M = beam.get_max_bending_moment()
    print(f"  Max Moment: {max_M/1000:.2f} kN*m at {pos_M:.2f} m")

    safety = beam.check_safety()
    print(f"\nSafety Check:")
    print(f"  Safety Factor: {safety['bending_safety_factor']:.2f}")
    print(f"  Status: {'SAFE' if safety['is_safe'] else 'NOT SAFE'}")

    return beam


def demo_ibeam():
    """
    Demo: I-Beam Section
    """
    print("\n" + "=" * 60)
    print("Demo 3: I-Beam Section Analysis")
    print("=" * 60)

    # Create I-beam section
    section = IBeamSection(
        h=0.400, b=0.200, tw=0.008, tf=0.013,
        name="HN400x200"
    )

    print(f"I-Beam Section: HN400x200")
    print(f"  h={section.h*1000:.0f}mm, b={section.b*1000:.0f}mm")
    print(f"  tw={section.tw*1000:.0f}mm, tf={section.tf*1000:.0f}mm")
    print(f"  Area: {section.get_area()*1e6:.0f} mm^2")
    print(f"  Iz: {section.get_moment_of_inertia('z')*1e12:.0f} mm^4")

    material = Steel('Q420')
    beam = Beam(
        length=8.0,
        section=section,
        material=material,
        name="I-Beam Demo"
    )

    beam.add_support(SimpleSupport(position=0))
    beam.add_support(SimpleSupport(position=8.0))
    beam.add_load(PointLoad(position=4.0, magnitude=100000))
    beam.add_load(UniformDistributedLoad(0, 8.0, 20000))

    beam.solve()

    print(f"\nResults:")
    max_M, pos_M = beam.get_max_bending_moment()
    print(f"  Max Moment: {max_M/1000:.2f} kN*m at {pos_M:.2f} m")
    max_v, pos_v = beam.get_max_deflection()
    print(f"  Max Deflection: {max_v*1000:.4f} mm")

    safety = beam.check_safety()
    print(f"\nSafety Check:")
    print(f"  Safety Factor: {safety['bending_safety_factor']:.2f}")
    print(f"  Status: {'SAFE' if safety['is_safe'] else 'NOT SAFE'}")

    return beam


def main():
    """
    Main function
    """
    print("=" * 60)
    print("Beam Object-Oriented Analysis Toolkit")
    print("=" * 60)
    print()
    print("Features:")
    print("  - Multiple section types: Rectangle, Circle, I-Beam, T-Beam")
    print("  - Material library: Steel, Concrete, Aluminum")
    print("  - Load types: Point load, UDL, Linear distributed, Moment")
    print("  - Support types: Fixed, Simple, Free, Pinned")
    print("  - Analysis: Internal forces, stresses, deformations")
    print("  - Visualization: Moment, shear, deflection diagrams")
    print("  - Safety check: Stress and deflection limits")
    print()

    # Run demos
    beam1 = demo_simple_beam()
    beam2 = demo_cantilever_beam()
    beam3 = demo_ibeam()

    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)
    print()
    print("For more examples, see the 'examples' directory")
    print("For visualization, run example scripts with matplotlib")


if __name__ == '__main__':
    main()