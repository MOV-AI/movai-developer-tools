import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="movai-tools",
    version="0.0.1-1",
    author="Mithun Kinarullathil",
    author_email="mithun@mov.ai",
    description="Tools to help the development of a project when using MOV.AI platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MithunKinarullathil/movai-tools",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[],
    entry_points={
        "console_scripts": ["movai-tools = movai_developer_tools.handler:handle"]
    },
)
