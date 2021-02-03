import os
import io
#import sys
from setuptools import find_packages, setup

## define setup variables
NAME='gerda'
VERSION='2.0'
DESCRIPTION='GEospacially Referenced Demographic Agent-based (GERDA) model for virus (SARS-CoV-2) transmission and disease (COVID-19) progression.'
LONG_description=''
AUTHOR=['Björn Goldenbogen',
        'Stephan O. Adler',
        'Oliver Bodeit',
        'Judith A.H. Wodke',
        'Aviv Korman',
        'Lasse Bonn',
        'Johanna E.L. Haffner',
        'Maxim Karnetzki',
        'Ivo Maintz',
        'Martin Seeger']
EMAIL=['bjoern.goldenbogen@hu-berlin.de','edda.klipp@hu-berlin.de']
URL='https://tbp-klipp.science/GERDA/code/'
REQUIRES_PYTHON='>=3.6.9' ## with this version everything got tested
REQUIRED=['geopandas>=0.8.1',
          'jupyter>=1.0.0',
          'matplotlib>=3.3.2',
          'numpy>=1.19.2',
          'osmnx==0.16.2',
          'pandas>=1.1.2',
          'rtree>=0.9.4',
          'seaborn>=0.11.0',
          'scipy>=1.5.2',
          'shapely>=1.7.1'] ## external packages as dependencies (versions have been tested, might also work with more recent versions)
LICENSE='GNU GPL v3.0'
SCRIPTS=[
       'scripts/generate_worlds.py',
       'scripts/sim_parallel.py',
       'scripts/read_geodata.py',
       'testing/testrunner.py'
       ]

## check for readme file, otherwise use description as long_description
here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        LONG_description = '\n' + f.read()
except FileNotFoundError:
    LONG_description = DESCRIPTION
LONG_description_content_type='text/markdown'

## if setup.py should be used for direct uploading, removal of previous builds should be added

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
   scripts=SCRIPTS
   )

"""
## in case classifiers shall be used, include code similar to the below example:
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
