#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='Todoflow',
    version='4.0',
    description='Todoflow - taskpaper in python',
    author='Piotr Wilczyński',
    author_email='wilczynski.pi@gmail.com',
    url='git+https://github.com/bevesce/TodoFlow',
    packages=['todoflow', 'todoflow.querying'],
    install_requires=[
        "ply",
    ],
    data_files=[('', ['todoflow/querying/parsetab.pickle'])]
)
