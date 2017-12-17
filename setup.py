#!/usr/bin/env python3

import os

from setuptools import setup, find_packages

setup(
    name         = 'pyexsmt',
    version      = '0.1',
    description  = 'Symbolic Execution Engine For Python Programs',
    author       = 'Federico Mora',
    author_email = 'fmorarocha@gmail.com',
    url          = 'https://github.com/FedericoAureliano/PyExSMT',
    scripts      = ['bin/pyexsmt'],
    packages     = find_packages(),
    package_dir  = {'pyexsmt': 'pyexsmt'},
    dependency_links=['https://github.com/pysmt/pysmt'],
    install_requires=[
        'mock',
        'graphviz',
        'pysmt>=0.7'
    ]
)