#!/usr/bin/env python

from glob import glob
from setuptools import setup, find_packages

setup(name='generator',
      version='0.2.0',
      description='Asprilo generator package',
      author='Philipp Obermeier, Thomas Otto',
      url='https://github.com/potassco/asprilo/tree/develop/generator',
      # * Dependencies handled by conda recipe ****************************************************
      # python_requires='>=3.6',
      # install_requires=['clingo>=5.3.0',
      #                   'pyyaml>=3.12'],
      # ********************************************************************************************
      packages=find_packages(),
      scripts=['scripts/gen'],
      data_files=[('encodings', glob('encodings/*'))],
     )
