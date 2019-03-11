#! /usr/bin/env python
from visualizer.control import VizControl
import sys

def main():
    control = VizControl()
    control.run()

if __name__ == '__main__':
    sys.exit(main())

