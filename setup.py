import setuptools

setuptools.setup(
    author="shawngmy",
    author_email="shawngmy@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    include_package_data=True,
    install_requires=["httpx", "pynacl"],
    name="pysui-sdk",
    packages=["pysui_sdk"],
    url="https://github.com/satisfywithmylife/sui_python_sdk",
    python_requires=">=3.7",
    version="1.0.4",
)
