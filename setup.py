import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# TODO Adapt your project configuration to your own project.
# The name of the package is the one to be used in runtime.
# The 'install_requires' is where you specify the package dependencies of your package. They will be automaticly installed, before your package.  # noqa: E501
setuptools.setup(
    name="movai-developer-tools",
    version="1.0.0-2",
    author="Mithun Kinarullathil",
    author_email="mithun@mov.ai",
    description="Scripts to improve development process when using MOV.AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MOV-AI/movai-developer-tools",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[],
    entry_points={
        "console_scripts": ["movros = movai_developer_tools.movros.handler:handle"]
    },
)
