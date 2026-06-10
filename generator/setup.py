#!/usr/bin/env python

from setuptools import setup, find_packages

from generator import release

setup(name='generator',
      version=release.__version__,
      description='Asprilo generator package',
      author='Philipp Obermeier, Thomas Otto',
      url='https://github.com/potassco/asprilo/tree/develop/generator',
      python_requires='>=3.9',
      install_requires=['clingo>=5.8.0',
                        'pyyaml>=6.0.0'],
      packages=find_packages(),
      entry_points={'console_scripts': ['gen = generator.__main__:main']},
      package_data={'generator': ['encodings/*']},
      )
