#!/usr/bin/env python3

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
    install_requires=[
        'mock',
        'graphviz',
        'pysmt>=0.7' #WE ARE ACTUALY USING 0.7.1dev!!
    ]
)