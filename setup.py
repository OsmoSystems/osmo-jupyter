#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="osmo_jupyter",
    version="0.0.1",
    author="Osmo Systems",
    author_email="dev@osmobot.com",
    description="Tools for accessing and processing OsmoBot data in an experimental context",
    url="https://www.github.com/osmosystems/python-jupyter-tools",
    packages=find_packages(),
    install_requires=[
        "ipython",
        "intervaltree",
        "numpy",
        "pandas",
        "petl",
        # Pin plotly version until skimage dependency is fixed
        # https://github.com/plotly/plotly.py/issues/1829
        "plotly==4.1.1",
        "pymysql",
        "requests",
        "scipy",
        "sqlalchemy",
    ],
    include_package_data=True,
)
