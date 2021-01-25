#!/usr/bin/env python

import os
import io
#import sys
from setuptools import find_package, setup

## define setup variables
NAME='gerda'
VERSION='2.0'
DESCRIPTION='A GEospacially Referenced Demographic Agent-based (GERDA) model for virus (SARS-CoV-2) transmission and disease (COVID-19) progression.'
LONG_description=''
AUTHOR=['Björn Goldenbogen', 'Stephan O. Adler', 'Oliver Bodeit', 'Judith A.H. Wodke', 'Aviv Korman', 'Lasse Bonn', 'Johanna E.L. Haffner', 'Maxim Karnetzki', 'Ivo Maintz', 'Martin Seeger']
EMAIL=['bjoern.goldenbogen@hu-berlin.de','edda.klipp@hu-berlin.de']
URL='https://tbp-klipp.science/GERDA/code/'
REQUIRES_PYTHON='>=3.2.0' ## check back with Ivo!
REQUIRED=['collections', 'copy', 'ctypes', 'glob', 'matplotlib', 'numpy', 'pandas', 'random', 'scipy'] ##external packages as dependencies
LICENSE='GNU GPL v3.0'

## check for readme file, otherwise use description as long_description
here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        LONG_description = '\n' + f.read()
except FileNotFoundError:
    LONG_description = DESCRIPTION
LONG_description_content_type='text/markdown'

## create setup using predefined variables
setup(
   name=NAME,
   version=VERSION,
   description=DESCRIPTION,
   long_description=LONG_description,
   long_description_content_type=LONG_description_content_type,
   author=AUTHOR,
   author_email=EMAIL,
   packages=[NAME], ##same as name
   install_requires=REQUIRED,
   #include_package_data=True,
   license=LICENSE,
   url=URL,
   )

"""
## what about classifiers, e.g.
   classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
"""
