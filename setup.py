""" Setup script for the collect_stata package."""
from setuptools import find_packages, setup

setup(
    name="collect_stata",
    version="0.0.1",
    url="https://github.com/ddionrails/collect_stata.git",
    description="Akkumulates data from stata files and writes to an open format.",
    long_description=open("./README.md").read(),
    packages=find_packages(),
    install_requires=["pandas >= 0.25.0"],
)
