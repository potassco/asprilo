#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='generator',
      version='0.2.1',
      description='Asprilo generator package',
      author='Philipp Obermeier, Thomas Otto',
      url='https://github.com/potassco/asprilo/tree/develop/generator',
      python_requires='>=3.9',
      install_requires=['clingo>=5.5.0',
                        'pyyaml>=5.4.1'],
      packages=find_packages(),
      entry_points={'console_scripts': ['gen = generator.__main__:main']},
      package_data={'generator': ['encodings/*']},
      )
