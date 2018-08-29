#!/usr/bin/env python
import os
from distutils.core import setup

setup(
    name='osmo_jupyter',
    version='0.0.1',
    author='Osmo Systems',
    author_email='dev@osmobot.com',
    description='Tools for accessing and processing OsmoBot data in an experimental context',
    url='https://www.github.com/osmosystems/python-jupyter-tools',
    packages=['osmo_jupyter'],
    install_requires=[
        'pandas',
        'numpy',
        'scipy',
        'pymysql',
        'petl',
        'intervaltree',
        'requests',
        'plotly==2',
    ],
    test_suite='pytest',
    tests_require=['pytest'],
    include_package_data=True
)
