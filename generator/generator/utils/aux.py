#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auxiliary Functions."""
import argparse

def check_positive(value):
    """Positive int check for argparse."""
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive int value!" % value)
    return ivalue

class SmartFormatter(argparse.HelpFormatter):
    """Conditional RawTextHelpFormatter."""
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)
