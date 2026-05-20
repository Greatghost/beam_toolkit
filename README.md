# 直梁面向对象解工具包

## 简介

直梁是工程结构中最常见、最基本的构件。在建筑、桥梁、机械等领域广泛应用。对直梁的受力分析是结构工程设计的核心内容。

本工具包是一个面向对象的Python软件包，用于求解直梁的力学问题，包括内力分析、应力计算和变形计算。

## 功能特点

- **多种截面类型支持**：矩形、圆形、工字形、T形等常用截面
- **材料库**：预定义钢材、混凝土、铝合金等常用材料
- **荷载类型**：集中力、均布荷载、线性分布荷载、集中弯矩
- **边界条件**：固定端、简支、悬臂、铰支撑等
- **计算功能**：
  - 支座反力计算
  - 内力分析（弯矩、剪力）
  - 应力计算（弯曲应力、剪应力）
  - 变形计算（挠度、转角）
- **可视化**：
  - 几何图（梁、荷载、支撑）
  - 弯矩图
  - 剪力图
  - 挠度图
  - 应力分布图
- **安全性检查**：应力验算、挠度限值检查

## 安装

```bash
pip install beam_toolkit
```

或直接克隆仓库：

```bash
git clone https://github.com/your-repo/beam_toolkit.git
```

## 快速开始

### 1. 创建简支梁

```python
from beam_toolkit import Beam, RectangleSection, Steel
from beam_toolkit import PointLoad, UniformDistributedLoad
from beam_toolkit import SimpleSupport
from beam_toolkit import BeamVisualizer

# 创建截面（矩形截面：宽0.2m，高0.4m）
section = RectangleSection(width=0.2, height=0.4)

# 创建材料（Q345钢材）
material = Steel('Q345')

# 创建梁（长度6m）
beam = Beam(length=6, section=section, material=material, name="简支梁示例")

# 添加支撑（两端简支）
beam.add_support(SimpleSupport(position=0))  # 左端简支
beam.add_support(SimpleSupport(position=6))  # 右端简支

# 添加荷载
beam.add_load(PointLoad(position=3, magnitude=50000))  # 中点50kN集中力
beam.add_load(UniformDistributedLoad(0, 6, 10000))  # 全跨10kN/m均布荷载

# 求解
results = beam.solve()

# 显示信息
print(beam.get_info())

# 可视化
visualizer = BeamVisualizer(beam)
visualizer.plot_all()

# 生成报告
report = visualizer.generate_report('beam_report.txt')
```

### 2. 创建悬臂梁

```python
from beam_toolkit import Beam, CircleSection, Aluminum
from beam_toolkit import PointLoad, FixedSupport, FreeEnd

# 创建圆形截面（直径0.1m）
section = CircleSection(diameter=0.1)

# 创建铝合金材料
material = Aluminum('6061-T6')

# 创建悬臂梁（长度2m）
beam = Beam(length=2, section=section, material=material, name="悬臂梁")

# 添加支撑
beam.add_support(FixedSupport(position=0))  # 左端固定
beam.add_support(FreeEnd(position=2))       # 右端自由

# 添加荷载
beam.add_load(PointLoad(position=2, magnitude=20000))  # 自由端20kN
beam.add_load(UniformDistributedLoad(0, 2, 5000))      # 全跨5kN/m

# 求解并可视化
beam.solve()
BeamVisualizer(beam).plot_all()
```

### 3. 使用工字形截面

```python
from beam_toolkit import IBeamSection, Steel

# 创建工字形截面（H型钢）
# h=0.4m, b=0.2m, tw=0.01m, tf=0.015m
section = IBeamSection(h=0.4, b=0.2, tw=0.01, tf=0.015)

# 计算截面特性
print(f"面积: {section.get_area():.6f} m²")
print(f"惯性矩: {section.get_moment_of_inertia():.9f} m⁴")
print(f"截面模量: {section.get_section_modulus():.6f} m³")
```

## API文档

### 核心类

#### Beam（梁类）

```python
Beam(length, section, material, name=None)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| length | float | 梁长度 (m) |
| section | Section | 截面对象 |
| material | Material | 材料对象 |
| name | str | 梁名称（可选） |

**主要方法**：
- `add_load(load)` - 添加荷载
- `add_support(support)` - 添加支撑
- `solve()` - 求解内力和变形
- `get_internal_forces()` - 获取内力结果
- `get_deformations()` - 获取变形结果
- `get_stresses()` - 获取应力结果
- `check_safety()` - 安全性检查
- `get_info()` - 获取信息摘要

### 截面类

#### RectangleSection（矩形截面）

```python
RectangleSection(width, height, name=None)
```

#### CircleSection（圆形截面）

```python
CircleSection(diameter=None, radius=None, name=None)
```

#### IBeamSection（工字形截面）

```python
IBeamSection(h, b, tw, tf, name=None)
```

| 参数 | 说明 |
|------|------|
| h | 总高度 (m) |
| b | 翼缘宽度 (m) |
| tw | 腹板厚度 (m) |
| tf | 翼缘厚度 (m) |

#### TBeamSection（T形截面）

```python
TBeamSection(h, b, tw, tf, name=None)
```

### 材料类

#### Material（材料基类）

```python
Material(name, elastic_modulus, yield_strength=None, ...)
```

#### Steel（钢材）

```python
Steel(steel_type='Q235', safety_factor=1.5)
```

支持类型：'Q235', 'Q345', 'Q420', 'A36', 'SS304'

#### Concrete（混凝土）

```python
Concrete(concrete_type='C30', safety_factor=1.4)
```

支持类型：'C25', 'C30', 'C35', 'C40', 'C50'

#### Aluminum（铝合金）

```python
Aluminum(aluminum_type='6061-T6', safety_factor=1.5)
```

支持类型：'6061-T6', '7075-T6', '2024-T4'

### 荷载类

#### PointLoad（集中力）

```python
PointLoad(position, magnitude, direction='down', name=None)
```

| 参数 | 说明 |
|------|------|
| position | 作用位置 (m) |
| magnitude | 荷载大小 (N) |
| direction | 'down' 或 'up' |

#### UniformDistributedLoad（均布荷载）

```python
UniformDistributedLoad(start_position, end_position, magnitude, direction='down', name=None)
```

| 参数 | 说明 |
|------|------|
| start_position | 起始位置 (m) |
| end_position | 结束位置 (m) |
| magnitude | 荷载集度 (N/m) |

#### MomentLoad（集中弯矩）

```python
MomentLoad(position, magnitude, direction='clockwise', name=None)
```

### 支撑类

#### FixedSupport（固定端）

```python
FixedSupport(position, name=None)
```

约束：垂直位移、转角、水平位移

#### SimpleSupport（简支）

```python
SimpleSupport(position, name=None)
```

约束：仅垂直位移

#### FreeEnd（自由端）

```python
FreeEnd(position, name=None)
```

无约束

### 可视化类

#### BeamVisualizer

```python
BeamVisualizer(beam, figsize=(12, 10))
```

**主要方法**：
- `plot_all()` - 绘制所有图形
- `plot_geometry()` - 绘制几何图
- `plot_moment()` - 绘制弯矩图
- `plot_shear()` - 绘制剪力图
- `plot_deflection()` - 绘制挠度图
- `plot_stress()` - 绘制应力图
- `generate_report()` - 生成分析报告

## 面向对象设计说明

### 类的设计原则

1. **封装性**：每个类封装了相关的属性和行为，通过清晰的方法接口访问
2. **继承性**：使用抽象基类定义接口，具体类继承实现
3. **多态性**：不同类型的截面、荷载、支撑通过统一的接口调用

### 类继承关系

```
Section (ABC)
├── RectangleSection
├── CircleSection
├── IBeamSection
└── TBeamSection

Material (ABC)
├── Steel
├── Concrete
└── Aluminum

Load (ABC)
├── PointLoad
├── DistributedLoad
│   ├── UniformDistributedLoad
│   ├── LinearDistributedLoad
│   └── GeneralDistributedLoad
└── MomentLoad

Support (ABC)
├── FixedSupport
├── SimpleSupport
│   ├── RollerSupport
└── FreeEnd

Solver (ABC)
├── AnalyticalSolver
```

## 依赖

- Python 3.8+
- numpy
- matplotlib

## 许可证

MIT License

## 作者

Beam Toolkit Team

## 版本历史

- v1.0.0 (2024): 初始版本
  - 支持基本截面类型
  - 支持常见材料
  - 支持简支梁、悬臂梁分析
  - 可视化功能