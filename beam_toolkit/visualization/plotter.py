"""
梁可视化绘图器
绘制梁的几何图、弯矩图、剪力图、挠度图等
"""

from typing import Dict, Optional, Tuple, List
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib

# 设置中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class BeamVisualizer:
    """
    梁可视化绘图器

    提供绘制梁的几何图、内力图、变形图等功能
    """

    def __init__(self, beam, figsize: Tuple[float, float] = (12, 10)):
        """
        初始化可视化器

        Args:
            beam: 梁对象
            figsize: 图形大小 (宽, 高)
        """
        self.beam = beam
        self.figsize = figsize
        self._fig = None
        self._axes = None

        # 确保梁已求解
        if not beam._solved:
            beam.solve()

    def plot_all(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制所有图形（几何图、弯矩图、剪力图、挠度图）

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        # 创建图形
        self._fig, self._axes = plt.subplots(4, 1, figsize=self.figsize)

        # 绘制各图
        self._plot_geometry(self._axes[0])
        self._plot_moment(self._axes[1])
        self._plot_shear(self._axes[2])
        self._plot_deflection(self._axes[3])

        # 调整布局
        plt.tight_layout()

        # 保存图形
        if save_path:
            self._fig.savefig(save_path, dpi=300, bbox_inches='tight')

        # 显示图形
        if show:
            plt.show()

        return self._fig

    def plot_geometry(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制梁的几何图（包含荷载和支撑）

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 3))
        self._plot_geometry(ax)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_moment(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制弯矩图

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 4))
        self._plot_moment(ax)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_shear(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制剪力图

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 4))
        self._plot_shear(ax)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_deflection(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制挠度图

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 4))
        self._plot_deflection(ax)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def _plot_geometry(self, ax: Axes) -> None:
        """
        绘制梁的几何图

        Args:
            ax: Axes对象
        """
        L = self.beam.length

        # 绘制梁
        ax.plot([0, L], [0, 0], 'b-', linewidth=3, label='梁')

        # 绘制支撑
        for support in self.beam.supports:
            pos = support.position
            support_type = support.get_constraint_type()

            if support_type == 'fixed':
                # 固定端：绘制固定符号
                ax.plot([pos, pos], [-0.3, 0], 'k-', linewidth=2)
                # 绘制固定端三角形（简化绘制）
                ax.add_patch(patches.Polygon([(pos-0.1, -0.3), (pos+0.1, -0.3), (pos, -0.15)],
                                          facecolor='gray', edgecolor='k'))

            elif support_type == 'simple':
                # 简支：绘制三角形支撑
                ax.add_patch(patches.Polygon([(pos-0.08, -0.25), (pos+0.08, -0.25), (pos, -0.15)],
                                          facecolor='white', edgecolor='k'))

            elif support_type == 'free':
                # 自由端：不绘制支撑符号
                pass

        # 绘制荷载
        for load in self.beam.loads:
            if load.get_load_type() == 'point_load':
                # 集中力：绘制箭头
                pos = load.position
                magnitude = load.get_total_load()
                # 箭头大小与荷载大小成比例
                arrow_length = min(0.5, max(0.1, abs(magnitude) / 10000))

                if magnitude > 0:  # 向下
                    ax.annotate('', xy=(pos, -arrow_length), xytext=(pos, 0.5),
                               arrowprops=dict(arrowstyle='->', color='red', lw=2))
                else:  # 向上
                    ax.annotate('', xy=(pos, 0.5), xytext=(pos, -arrow_length),
                               arrowprops=dict(arrowstyle='->', color='red', lw=2))

                # 标注荷载大小
                ax.text(pos, 0.55, f'{abs(magnitude)/1000:.1f}kN', ha='center', fontsize=8)

            elif load.get_load_type() == 'uniform_distributed_load':
                # 均布荷载：绘制均匀分布的箭头
                start = load.start_position
                end = load.end_position
                w = abs(load.get_total_load() / load.length)

                # 绘制分布箭头
                n_arrows = max(3, int((end - start) / L * 10))
                positions = np.linspace(start, end, n_arrows)

                for p in positions:
                    arrow_length = 0.3
                    ax.annotate('', xy=(p, -arrow_length), xytext=(p, 0.3),
                               arrowprops=dict(arrowstyle='->', color='orange', lw=1))

                # 绘制荷载线
                ax.plot([start, end], [0.3, 0.3], 'orange', linewidth=1)
                ax.text((start + end)/2, 0.4, f'{abs(load.magnitude)/1000:.1f}kN/m',
                       ha='center', fontsize=8, color='orange')

            elif load.get_load_type() == 'moment_load':
                # 集中弯矩：绘制弧形箭头
                pos = load.position
                ax.annotate('', xy=(pos + 0.2, 0.3), xytext=(pos - 0.2, 0.3),
                           arrowprops=dict(arrowstyle='->', color='purple', lw=2,
                                          connectionstyle='arc3,rad=0.3'))
                ax.text(pos, 0.45, f'{abs(load.get_total_load())/1000:.1f}kN*m',
                       ha='center', fontsize=8, color='purple')

        # 设置图形属性
        ax.set_xlim(-0.5, L + 0.5)
        ax.set_ylim(-1, 1)
        ax.set_xlabel('位置 (m)')
        ax.set_title(f'{self.beam.name} - 几何图 ({self.beam.get_beam_type()})')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        # 标注梁长度
        ax.text(L/2, -0.6, f'L = {L:.2f}m', ha='center', fontsize=10)

        # 标注截面和材料信息
        section_info = f"截面: {self.beam.section.name}"
        material_info = f"材料: E={self.beam.material.elastic_modulus/1e9:.1f}GPa"
        ax.text(L + 0.3, 0.5, section_info, fontsize=9)
        ax.text(L + 0.3, 0.3, material_info, fontsize=9)

    def _plot_moment(self, ax: Axes) -> None:
        """
        绘制弯矩图

        按照用户规则：
        - 顺时针弯矩为正（y轴向下为正方向）
        - 弯矩图y轴反向：上为负，下为正

        Args:
            ax: Axes对象
        """
        results = self.beam.get_internal_forces()
        x = results['position']
        M = results['moment']

        # 弯矩图绘制在受拉面，y轴反向（上负下正）
        # 绘制弯矩曲线（正值向下）
        ax.plot(x, -M / 1000, 'b-', linewidth=2, label='弯矩 M')

        # 填充弯矩区域
        # 正弯矩（顺时针，上表面受拉）填在下方
        # 负弯矩（逆时针，下表面受拉）填在上方
        ax.fill_between(x, 0, -M / 1000, where=M >= 0, alpha=0.3, color='red', label='正弯矩(顺时针,上表面受拉)')
        ax.fill_between(x, 0, -M / 1000, where=M < 0, alpha=0.3, color='blue', label='负弯矩(逆时针,下表面受拉)')

        # 标注最大弯矩
        max_M, pos_M = self.beam.get_max_bending_moment()
        ax.plot(pos_M, -max_M / 1000, 'ko', markersize=8)
        ax.annotate(f'M_max = {max_M/1000:.2f}kN*m', xy=(pos_M, -max_M/1000),
                   xytext=(pos_M + 0.5, -max_M/1000 - 2),
                   arrowprops=dict(arrowstyle='->', color='k'), fontsize=10)

        # 绘制零点
        ax.axhline(y=0, color='k', linewidth=0.5)

        # 反转y轴（上负下正）
        ax.invert_yaxis()

        # 设置图形属性
        ax.set_xlabel('位置 x (m)')
        ax.set_ylabel('弯矩 M (kN*m)')
        ax.set_title('弯矩图 (顺时针为正，y轴上负下正)')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        # 标注弯矩方向说明
        ax.text(0.02, 0.02, '注：顺时针弯矩为正，弯矩图画在受拉面', transform=ax.transAxes,
               fontsize=9, verticalalignment='bottom')

    def _plot_shear(self, ax: Axes) -> None:
        """
        绘制剪力图

        Args:
            ax: Axes对象
        """
        results = self.beam.get_internal_forces()
        x = results['position']
        V = results['shear']

        # 绘制剪力曲线
        ax.plot(x, V / 1000, 'g-', linewidth=2, label='剪力 V')

        # 填充剪力区域
        ax.fill_between(x, 0, V / 1000, alpha=0.3, color='green')

        # 标注最大剪力
        max_V, pos_V = self.beam.get_max_shear_force()
        ax.plot(pos_V, max_V / 1000, 'ko', markersize=8)
        ax.annotate(f'V_max = {max_V/1000:.2f}kN', xy=(pos_V, max_V/1000),
                   xytext=(pos_V + 0.5, max_V/1000 * 1.1),
                   arrowprops=dict(arrowstyle='->', color='k'), fontsize=10)

        # 绘制零点
        ax.axhline(y=0, color='k', linewidth=0.5)

        # 标注支座反力
        reactions = self.beam.get_reaction_forces()
        if 'left' in reactions:
            ax.text(0, reactions['left']['reaction']/1000 + 0.5,
                   f'R_A={reactions["left"]["reaction"]/1000:.2f}kN', fontsize=9)
        if 'right' in reactions:
            ax.text(self.beam.length, reactions['right']['reaction']/1000 + 0.5,
                   f'R_B={reactions["right"]["reaction"]/1000:.2f}kN', fontsize=9)

        # 设置图形属性
        ax.set_xlabel('位置 x (m)')
        ax.set_ylabel('剪力 V (kN)')
        ax.set_title('剪力图')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

    def _plot_deflection(self, ax: Axes) -> None:
        """
        绘制挠度图

        Args:
            ax: Axes对象
        """
        results = self.beam.get_deformations()
        x = results['position']
        v = results['deflection']

        # 绘制挠度曲线
        # 挠度放大显示（因为实际挠度很小）
        scale_factor = 1  # 显示比例

        ax.plot(x, v * 1000 * scale_factor, 'm-', linewidth=2, label='挠度 v')

        # 填充挠度区域
        ax.fill_between(x, 0, v * 1000 * scale_factor, alpha=0.3, color='magenta')

        # 标注最大挠度
        max_v, pos_v = self.beam.get_max_deflection()
        ax.plot(pos_v, max_v * 1000 * scale_factor, 'ko', markersize=8)
        ax.annotate(f'v_max = {max_v*1000:.4f}mm\n({max_v/self.beam.length*1000:.4f}‰L)',
                   xy=(pos_v, max_v*1000*scale_factor),
                   xytext=(pos_v + 0.5, max_v*1000*scale_factor * 1.2),
                   arrowprops=dict(arrowstyle='->', color='k'), fontsize=10)

        # 绘制原始梁位置
        ax.axhline(y=0, color='b', linewidth=1, linestyle='--', label='原始位置')

        # 绘制变形限值线
        deflection_limit = self.beam.length / 250 * 1000  # L/250, 单位mm
        ax.axhline(y=deflection_limit, color='r', linewidth=1, linestyle=':', label=f'限值 L/250={deflection_limit:.2f}mm')
        ax.axhline(y=-deflection_limit, color='r', linewidth=1, linestyle=':',)

        # 设置图形属性
        ax.set_xlabel('位置 x (m)')
        ax.set_ylabel('挠度 v (mm)')
        ax.set_title('挠度图')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

    def plot_stress(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制应力分布图

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        results = self.beam.get_stresses()
        x = results['position']
        sigma = results['bending_stress']

        fig, ax = plt.subplots(figsize=(12, 4))

        # 绘制应力曲线
        ax.plot(x, sigma / 1e6, 'c-', linewidth=2, label='最大弯曲应力 σ')

        # 绘制许用应力线
        allowable = self.beam.material.get_allowable_stress()
        ax.axhline(y=allowable / 1e6, color='r', linewidth=2, linestyle='--',
                  label=f'许用应力 σ_allow={allowable/1e6:.1f}MPa')
        ax.axhline(y=-allowable / 1e6, color='r', linewidth=2, linestyle='--')

        # 填充安全区域
        ax.fill_between(x, -allowable/1e6, allowable/1e6, alpha=0.2, color='green', label='安全区域')

        # 设置图形属性
        ax.set_xlabel('位置 x (m)')
        ax.set_ylabel('应力 σ (MPa)')
        ax.set_title('弯曲应力分布图')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def plot_rotation(self, save_path: Optional[str] = None, show: bool = True) -> Figure:
        """
        绘制转角图

        Args:
            save_path: 保存路径（可选）
            show: 是否显示图形

        Returns:
            Figure对象
        """
        results = self.beam.get_deformations()
        x = results['position']
        theta = results['rotation']

        fig, ax = plt.subplots(figsize=(12, 4))

        # 绘制转角曲线
        ax.plot(x, theta * 1000, 'orange', linewidth=2, label='转角 θ')

        # 绘制零点
        ax.axhline(y=0, color='k', linewidth=0.5)

        # 设置图形属性
        ax.set_xlabel('位置 x (m)')
        ax.set_ylabel('转角 θ (×10⁻³ rad)')
        ax.set_title('转角图')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        if show:
            plt.show()

        return fig

    def generate_report(self, save_path: Optional[str] = None) -> str:
        """
        生成分析报告

        Args:
            save_path: 报告保存路径（可选）

        Returns:
            报告文本
        """
        # 获取梁信息
        info = self.beam.get_info()

        # 获取安全性检查结果
        safety = self.beam.check_safety()

        # 组装报告
        report_lines = [
            "=" * 60,
            "梁力学分析报告",
            "=" * 60,
            "",
            info,
            "",
            "=" * 60,
            "荷载信息",
            "=" * 60,
        ]

        for load in self.beam.loads:
            report_lines.append(f"  {load}")

        report_lines.extend([
            "",
            "=" * 60,
            "支撑信息",
            "=" * 60,
        ])

        for support in self.beam.supports:
            report_lines.append(f"  {support}")

        report_lines.extend([
            "",
            "=" * 60,
            "支座反力",
            "=" * 60,
        ])

        reactions = self.beam.get_reaction_forces()
        for key, value in reactions.items():
            if isinstance(value, dict):
                pos = value.get('position', 0)
                if 'reaction' in value:
                    report_lines.append(f"  {key} @ {pos:.2f}m: R = {value['reaction']/1000:.2f} kN")
                if 'vertical_reaction' in value:
                    report_lines.append(f"  {key} @ {pos:.2f}m: R_v = {value['vertical_reaction']/1000:.2f} kN")
                if 'moment_reaction' in value:
                    report_lines.append(f"  {key} @ {pos:.2f}m: M = {value['moment_reaction']/1000:.2f} kN*m")

        report_lines.extend([
            "",
            "=" * 60,
            "最大值",
            "=" * 60,
            f"  最大弯矩: {self.beam.get_max_bending_moment()[0]/1000:.2f} kN*m",
            f"  最大剪力: {self.beam.get_max_shear_force()[0]/1000:.2f} kN",
            f"  最大挠度: {self.beam.get_max_deflection()[0]*1000:.4f} mm",
            "",
            "=" * 60,
            "安全性检查",
            "=" * 60,
            f"  最大弯曲应力: {safety['max_bending_stress']/1e6:.2f} MPa",
            f"  许用应力: {safety['allowable_stress']/1e6:.2f} MPa",
            f"  安全系数: {safety['bending_safety_factor']:.2f}",
            f"  安全状态: {'安全' if safety['is_safe'] else '不安全'}",
            f"  挠度限值: L/250 = {safety['deflection_limit']*1000:.2f} mm",
            f"  实际挠度: {safety['max_deflection']*1000:.4f} mm",
            f"  挠度检查: {'满足' if safety['deflection_safe'] else '不满足'}",
            "",
            "=" * 60,
            "结论",
            "=" * 60,
            f"  该梁{'满足安全要求，可以使用。' if safety['is_safe'] and safety['deflection_safe'] else '不满足安全要求，需要重新设计。'}",
            "",
        ])

        report = '\n'.join(report_lines)

        # 保存报告
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)

        return report