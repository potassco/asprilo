#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auxiliary Functions."""
import argparse

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue
