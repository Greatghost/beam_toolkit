"""
setup.py
用于安装直梁面向对象解工具包
"""

from setuptools import setup, find_packages

setup(
    name='beam_toolkit',
    version='1.0.0',
    description='直梁面向对象解工具包 - 用于直梁力学分析的Python软件包',
    author='Beam Toolkit Team',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.20.0',
        'matplotlib>=3.4.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    keywords='beam analysis structural engineering mechanics',
)