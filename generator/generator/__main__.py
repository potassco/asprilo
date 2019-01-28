#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entry Point for Command-Line Invocation."""

import sys

from generator.control import Control

def main():
    """Main."""
    Control().run()

if __name__ == '__main__':
    sys.exit(main())
