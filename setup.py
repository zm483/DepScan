# setup.py
from setuptools import setup, find_packages

setup(
    name='depscan',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyGithub>=2.0.0',
        'click>=8.0.0',
        'rich>=10.0.0',
    ],
    entry_points={
        'console_scripts': [
            'depscan=depscan.cli:scan',  # 将命令'depscan'指向函数
        ],
    },
    author=' 名字',
    description='一个开源项目弃用风险扫描器',
    keywords='github, risk, scanner, opensource',
)