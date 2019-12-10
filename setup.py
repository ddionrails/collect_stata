""" Setup script for the collect_stata package."""
from setuptools import find_packages, setup

# Package meta-data.
NAME = "collect_stata"
DESCRIPTION = "Accumulates data from stata files and writes to an open format."
URL = "https://github.com/ddionrails/collect_stata"
EMAIL = "mpahl@diw.de"
AUTHOR = "Marius Pahl"
REQUIRES_PYTHON = ">=3.8.0"
VERSION = "0.0.1"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: BSD License",
]
KEYWORDS = ["stata", "dta", "tdp"]
LICENSE = "BSD 3-Clause"

setup(
    name=NAME,
    version=VERSION,
    url=URL,
    description=DESCRIPTION,
    long_description=open("./README.rst").read(),
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(),
    install_requires=["pandas >= 0.25.0"],
    entry_points={"console_scripts": ["collect_stata = collect_stata.__main__:main"]},
    license=LICENSE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
)
