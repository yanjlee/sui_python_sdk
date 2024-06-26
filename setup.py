import setuptools
import shutil

# 删除dist/目录
shutil.rmtree('dist', ignore_errors=True)

setuptools.setup(
    name="pysui_utils",
    version="1.0.1",
    author="yanjlee",
    author_email="yanjlee@163.com", 
    description="This project is dedicated to sharing and teaching the fundamentals and techniques of sui crypto engineering. Crypto engineering involves analyzing how websites and web applications work, and cracking or modifying existing code to achieve specific objectives. This project includes a series of tutorials, practical tools, and case studies aimed at helping developers, security researchers, and enthusiasts understand how to effectively reverse engineer web technologies.",  # 模块简介
    install_requires=[
        'requests',
        'faker',
        'execjs',
        'loguru',
        'base64',
        'hashlib',
        'Crypto',
        "httpx", 
        "pynacl"
    ],
    long_description=open(r'readme.md', encoding='utf-8').read(),  # 读取readme自述文件
    long_description_content_type="text/markdown",
    url="https://github.com/yanjlee/sui_python_sdk",  # 模块github地址
    packages=setuptools.find_packages(),     # 自动列出项目下的包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",   # 开源许可证
        "Operating System :: OS Independent",      # 这里的定义是系统无关（全平台兼容），如果你的包只能在部分特定系统上运行，需要修改。
    ],
)
