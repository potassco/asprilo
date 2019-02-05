#!/usr/bin/env python

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
      entry_points={'console_scripts': ['gen = generator.__main__:main']},
      package_data={'generator': ['encodings/*']},
     )
