#!/usr/bin/env python
from setuptools import setup

setup(
    name='osmo_jupyter',
    version='0.0.1',
    author='Osmo Systems',
    author_email='dev@osmobot.com',
    description='Tools for accessing and processing OsmoBot data in an experimental context',
    url='https://www.github.com/osmosystems/python-jupyter-tools',
    packages=['osmo_jupyter'],
    install_requires=[
        'intervaltree',
        'numpy',
        'pandas',
        'petl',
        'plotly >= 3, < 4',
        'pymysql',
        'requests',
        'scipy',
        'sqlalchemy',
    ],
    include_package_data=True
)
