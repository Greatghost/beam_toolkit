"""
示例主入口
运行所有示例
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_examples():
    """
    运行所有示例
    """
    print("=" * 60)
    print("直梁面向对象解工具包 - 示例演示")
    print("=" * 60)
    print()

    examples = [
        ("示例1：简支梁分析", "example1_simple_beam"),
        ("示例2：悬臂梁分析", "example2_cantilever_beam"),
        ("示例3：工字形截面梁", "example3_ibeam"),
        ("示例4：多种荷载组合", "example4_combined_loads"),
        ("示例5：自定义材料", "example5_custom_material"),
    ]

    print("可用示例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print()

    # 选择示例
    try:
        choice = input("请选择要运行的示例（输入数字，或输入'all'运行全部）：")

        if choice.lower() == 'all':
            # 运行全部示例
            for i, (name, module_name) in enumerate(examples, 1):
                print()
                print(f"运行 {name}...")
                print("-" * 60)
                module = __import__(module_name)
                module.main()
        else:
            # 运行单个示例
            idx = int(choice)
            if 1 <= idx <= len(examples):
                name, module_name = examples[idx - 1]
                print(f"运行 {name}...")
                print("-" * 60)
                module = __import__(module_name)
                module.main()
            else:
                print("无效的选择")

    except ValueError:
        print("无效的输入")
    except KeyboardInterrupt:
        print("\n用户中断")


if __name__ == '__main__':
    run_all_examples()