#!/usr/bin/env python

from setuptools import setup

setup(name='visualizer',
      version='0.3.0',
      description='Asprilo visualizer package',
      author='Thomas Otto, Philipp Obermeier',
      url='https://github.com/potassco/asprilo/tree/develop/visualizer',
      python_requires='>=3.9',
      install_requires=['clingo>=5.8.0',
                        'PyQt5>=5.15.0'],
      packages=['visualizer'],
      entry_points={'console_scripts': [
                           'viz = visualizer.__main__:main',
                           'viz-solver = visualizer.solver:main',
                           'viz-simulator = visualizer.simulator:main']},
      )
