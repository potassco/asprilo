#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test instance generator'''
import subprocess
import sys
import os
import shlex
import argparse

def define_cases():

    cases = {}

    ## Some Standard Cases
    _cases = cases["standard_cases"] = []

    # 10x10 grid, 5 robots, 16 shelves, 4 stations, 4 products,  32 product units total, 8 orders
    _cases.append("1 -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    #
    _cases.append("2 -x 5 -y 5 -r 3 -s 8 -p 1 -P 2 -u 8 -o 4 -R --oap")

    #
    _cases.append("3 -x 12 -y 12 -r 6 -s 16 -p 5 -P 5 -u 32 -o 8 -R -H --oap")

    #
    _cases.append("4 -x 10 -y 10 -r 4 -s 12 -p 3 -P 3 -u 20 -o 5 -R -H --oap")

    #
    _cases.append("5 -x 8 -y 8 -r 4 -s 10 -p 2 -P 3 -u 16 -o 4 -R -H --oap")

    #
    _cases.append("6 -x 14 -y 14 -r 7 -s 20 -p 6 -P 5 -u 48 -o 12 -R -H --oap")

    #
    _cases.append("7 -x 9 -y 9 -r 4 -s 14 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    #
    _cases.append("8 -x 10 -y 10 -r 4 -s 15 -p 3 -P 5 -u 24 -o 6 -R -H --oap")

    #
    _cases.append("9 -x 10 -y 10 -r 5 -s 20 -p 5 -P 5 -u 48 -o 6 -R -H --oap")

    #
    _cases.append("10 -x 10 -y 10 -r 5 -s 20 -p 6 -P 5 -u 10 -o 5 -R -H --oap")

    ## Tiny Tests
    _cases = cases["tiny_cases"] = []

    _cases.append("1x2a -x 1 -y 2 -r 1 -s 1 -p 1 -P 1 -u 1 -o 1 --oap")
    _cases.append("1x2b -x 1 -y 2 -r 1 -s 1 -p 1 -P 2 -u 2 -o 2 --oap")
    _cases.append("1x2c -x 1 -y 2 -r 1 -s 1 -p 1 -P 2 -u 4 -o 2 --oap")

    _cases.append("2x2a -x 2 -y 2 -r 1 -s 1 -p 1 -P 1 -u 1 -o 1 -R --oap")
    _cases.append("2x2b -x 2 -y 2 -r 2 -s 2 -p 1 -P 2 -u 2 -o 2 -R --oap")
    _cases.append("2x2c -x 2 -y 2 -r 2 -s 2 -p 1 -P 2 -u 4 -o 2 -R --oap")

    _cases.append("3x3a -x 3 -y 3 -r 1 -s 1 -p 1 -P 1 -u 1 -o 1 -R --oap")
    _cases.append("3x3b -x 3 -y 3 -r 2 -s 2 -p 1 -P 2 -u 2 -o 2 -R --oap")
    _cases.append("3x3c -x 3 -y 3 -r 2 -s 2 -p 1 -P 2 -u 4 -o 2 -R --oap")

    _cases.append("4x4a -x 4 -y 4 -r 2 -s 3 -p 1 -P 2 -u 4 -o 2 -R --oap")
    _cases.append("4x4b -x 4 -y 4 -r 2 -s 6 -p 2 -P 4 -u 8 -o 4 -R --oap")
    _cases.append("4x4c -x 4 -y 4 -r 3 -s 6 -p 2 -P 6 -u 12 -o 6 -R --oap")


    ## Grid Tests
    _cases = cases["grid_scaling"] = []

    # extreme
    # _cases.append("extreme -x 48 -y 48 -r 16 -s 64 -p 12 -P 8 -u 128 -o 32 -R -H --oap")

    # huge
    _cases.append("huge  -x 26 -y 26 -r 5 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # wide
    _cases.append("wide -x 8 -y 30 -r 5 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # small
    _cases.append("small -x 3 -y 3 -r 1 -s 2 -p 1 -P 2 -u 2 -o 2")

    # tight
    _cases.append("tight  -x 10 -y 2 -r 5 -s 12 -p 2 -P 4 -u 16 -o 4 -R")


    ## Robots
    _cases = cases["robots_scaling"] = []

    # extreme
    # _cases.append("extreme -x 28 -y 28 -r 48 -s 64 -p 12 -P 8 -u 128 -o 32 -R -H --oap")

    # many
    _cases.append("many -x 10 -y 10 -r 16 -s 16 -p 4 -P 4 -u 32 -o 16 -R -H --oap")

    # overwhelmed
    _cases.append("overwhelmed -x 10 -y 10 -r 8 -s 16 -p 1 -P 1 -u 16 -o 16 -R --oap")

    # medium
    _cases.append("medium -x 10 -y 10 -r 8 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # few
    _cases.append("few -x 10 -y 10 -r 2 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")


    ## Shelves
    _cases = cases["shelves_scaling"] = []

    # eXtreme
    # _cases.append("eXtreme -x 28 -y 28 -r 16 -s 128 -p 12 -P 8 -u 128 -o 32 -R -H --oap")

    # many
    _cases.append("many -x 10 -y 10 -r 5 -s 32 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # medium
    _cases.append("medium -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # stuck
    # _cases.append("stuck -x 5 -y 5 -r 5 -s 25 -p 2 -P 5 -u 25 -o 8 -R --oap")

    # few
    _cases.append("few -x 10 -y 10 -r 5 -s 8 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # one
    _cases.append("one -x 5 -y 5 -r 5 -s 1 -p 15 -P 5 -u 25 -o 8 -R --oap")


    ## Picking Stations
    _cases = cases["pickingstations_scaling"] = []

    # eXtreme
    # _cases.append("eXtreme -x 28 -y 28 -r 16 -s 64 -p 56 -P 8 -u 128 -o 32 -R -H --oap")

    # many
    _cases.append("many -x 10 -y 10 -r 5 -s 16 -p 8 -P 4 -u 32 -o 8 -R -H --oap")

    # few
    _cases.append("few -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 32 -o 8 -R -H --oap")

    # one
    _cases.append("one -x 10 -y 10 -r 5 -s 16 -p 1 -P 4 -u 32 -o 8 -R -H --oap")


    ## Products
    _cases = cases["products-units-orders_scaling"] = []

    # eXtreme
    # _cases.append("eXtreme -x 28 -y 28 -r 16 -s 64 -p 12 -P 128 -u 256 -o 64 -R -H --oap")

    # many units
    _cases.append("many -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 64 -o 8 -R -H --oap")

    # few units
    _cases.append("few -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 4 -o 8 -R -H --oap")

    # many common units
    _cases.append("many_common -x 10 -y 10 -r 5 -s 16 -p 4 -P 1 -u 64 -o 8 -R -H --oap")

    # many rare units
    _cases.append("many_rare -x 10 -y 10 -r 5 -s 16 -p 4 -P 64 -u 64 -o 8 -R -H --oap")

    # all units ordered
    _cases.append("all_ordered -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 32 -o 32 -R -H --oap")

    # few units ordered
    _cases.append("few_ordered -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 32 -o 4 -R -H --oap")

    return cases

def gen_instances(cases, args):

    if args.cats:
        cases_items = {cat : cases[cat] for cat in args.cats}.items()
    else:
        cases_items = cases.items()
    if args.split:
        split = '--split {0} {1}'.format(args.split[0], args.split[1])
    else:
        split = ''
    for cat, _cases in cases_items:
        for case in _cases:
            case_dir, case_pars = case.split(None, 1)
            dest_dir = '{directory}/{cat}/{case_dir}'.format(directory=args.directory,
                                                             cat=cat,
                                                             case_dir=case_dir)
            if os.path.isdir(dest_dir):
                print '\n**** ' + dest_dir + ' exists, skipping! *****\n'
            else:
                command = shlex.split(
                    '''python ./ig.py
                    -t {threads}
                    -w {wait}
                    -N {models}
                    {split}
                    -d {dest_dir}
                    {case_pars}'''.format(threads=args.threads,
                                          wait=args.wait,
                                          models=args.models,
                                          split=split,
                                          dest_dir=dest_dir,
                                          case_pars=case_pars))
                print command
                subprocess.call(command)

def main():
    parser = argparse.ArgumentParser(
        usage='Extracts facts from json file read from stdin or give as argument')
    parser.add_argument('-c', '--cats', nargs='*', help='optional list of benchmark categories to create')
    parser.add_argument('-d', '--directory', type=str, default='generatedInstances',
                        help="the directory to safe the files")
    parser.add_argument('-t', '--threads', type=int, help='number of clasp threads', default=1)
    parser.add_argument('-w' , '--wait', type=int,
                        help='time to wait in seconds before solving is aborted if not finished yet', default=300)
    parser.add_argument('-N', '--models', type=int, help='number of instances', default=10)
    parser.add_argument('--split', nargs=2, type=int,
                        help='''splits instances into warehouse and
                                  order-related facts; takes as arguments 1.)
                                  the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.''')
    args = parser.parse_args()
    gen_instances(define_cases(), args)

sys.exit(main())
