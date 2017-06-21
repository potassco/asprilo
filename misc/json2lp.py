#!/usr/bin/env python
"""Translates clingo's Json fact format to regular *.lp format.

"""

import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(usage='Extracts facts from json file read from stdin or give as argument')
    parser.add_argument('jfile', nargs='?', help='Json file')
    args = parser.parse_args()
    if args.jfile:
        data = json.load(open(args.jfile))
    else:
        data = json.load(sys.stdin)

    for fact in data['Call'][-1]['Witnesses'][0]['Value']:
        print fact + "."

sys.exit(main())
