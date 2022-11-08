import setuptools

github_source_dependencies = [

]
with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()


setuptools.setup(
    name="firstserve",
    version="0.1",
    author="Ilja von Hoessle",
    author_email="",
    description="Generation of a tennis database to perform statistical analysis on player performances and match outcome predictions.",
    long_description=long_description,
    url="https://github.com/iljabvh/firstserve",
    packages=setuptools.find_packages(),
    install_requires=required,
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
)
