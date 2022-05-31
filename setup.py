import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="movai-developer-tools",
    version="0.0.1-1",
    author="Mithun Kinarullathil",
    author_email="mithun@mov.ai",
    description="Scripts to improve development process when using MOV.AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MOV-AI/movai-developer-tools",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=["docker==5.0.3"],
    entry_points={
        "console_scripts": [
            "movros = movai_developer_tools.movros.handler:handle",
            "movmisc = movai_developer_tools.movmisc.handler:handle",
            "movbkp = movai_developer_tools.movbkp.handler:handle",
            "movcontext = movai_developer_tools.movcontext.handler:handle",
        ]
    },
)
