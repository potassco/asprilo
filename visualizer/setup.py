#!/usr/bin/env python

from setuptools import setup

setup(name='visualizer',
      version='0.2.4',
      description='Asprilo visualizer package',
      author='Thomas Otto, Philipp Obermeier',
      url='https://github.com/potassco/asprilo/tree/develop/visualizer',
      python_requires='>=3.9',
      install_requires=['clingo>=5.5.0',
                        'PyQt5>=5.9'],
      packages=['visualizer'],
      entry_points={'console_scripts': [
                           'viz = visualizer.__main__:main',
                           'viz-solver = visualizer.solver:main',
                           'viz-simulator = visualizer.simulator:main']},
      )
