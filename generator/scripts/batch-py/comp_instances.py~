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

    ## Standard Cases
    _cases = cases["standard_cases"] = []

    # 10x10 grid, 5 robots, 16 shelves, 4 stations, 4 products, 32 product units total,
    # 8 orders, 2-4 order lines, all products ordered at least once
    _cases.append("tiny -x 7 -y 7 -r 2 -s 6 -p 1 -P 3 -u 12 -o 3 --olmin 1 --olmax 2 --oap -R -H")
    _cases.append("small -x 8 -y 8 -r 3 -s 10 -p 2 -P 4 -u 16 -o 4 --olmin 2 --olmax 4 --oap -R -H")
    _cases.append("medium -x 10 -y 10 -r 5 -s 16 -p 4 -P 6 -u 24 -o 6 --olmin 2 --olmax 4 --oap -R -H")
    # _cases.append("medium -x 10 -y 10 -r 5 -s 16 -p 4 -P 8 -u 32 -o 6 --olmin 2 --olmax 4 --oap -R -H")
    # _cases.append("medium -x 10 -y 10 -r 5 -s 16 -p 4 -P 8 -u 32 -o 8 --olmin 2 --olmax 4 --oap -R -H")
    _cases.append("large -x 12 -y 12 -r 7 -s 32 -p 6 -P 18 -u 96 -o 12 --olmin 2 --olmax 4 --oap -R -H")
    # _cases.append("huge -x 16 -y 16 -r 10 -s 64 -p 8 -P 24 -u 128 -o 16 --olmin 2 --olmax 4 --oap -R -H")

    ## 'Non-Standard' Cases, i.e., Standard Cases w/o Reachability and Highway
    _cases = cases["nonstandard_cases"] = []
    _cases.append("tiny -x 7 -y 7 -r 2 -s 6 -p 1 -P 3 -u 12 -o 3 --olmin 1 --olmax 2 --oap")
    _cases.append("small -x 8 -y 8 -r 3 -s 10 -p 2 -P 4 -u 16 -o 4 --olmin 2 --olmax 4 --oap")
    _cases.append("medium -x 10 -y 10 -r 5 -s 16 -p 4 -P 6 -u 24 -o 6 --olmin 2 --olmax 4 --oap")
    _cases.append("large -x 12 -y 12 -r 7 -s 32 -p 6 -P 18 -u 96 -o 12 --olmin 2 --olmax 4 --oap")
    #_cases.append("huge -x 20 -y 20 -r 20 -s 128 -p 16 -P 24 -u 256 -o 32 --olmin 2 --olmax 4 --oap")

    ## Shelves vs products
    _cases = cases["shelves_product_scaling"] = []
    _cases.append("many_shelves_few_products -x 10 -y 10 -r 5 -s 32 -p 4 -P 4 -u 16 -o 8 --olmin 2 --olmax 4 --oap -R -H")
    _cases.append("many_shelves_many_products -x 10 -y 10 -r 5 -s 32 -p 4 -P 12 -u 48 -o 8 --olmin 2 --olmax 4 --oap -R -H")
    _cases.append("few_shelves_many_products -x 10 -y 10 -r 5 -s 8 -p 4 -P 12 -u 48 -o 8 --olmin 2 --olmax 4 --oap -R -H")

    ## Picking Stations Scaling
    _cases = cases["pickingstations_scaling"] = []
    # one picking station, medium standard case
    _cases.append("one -x 10 -y 10 -r 5 -s 16 -p 1 -P 4 -u 32 -o 8 --olmin 2 --olmax 4 --oap -R -H")
    # few picking stations, huge standard case
    _cases.append("few -x 20 -y 20 -r 20 -s 128 -p 2 -P 24 -u 256 -o 32 --olmin 2 --olmax 4 --oap -R -H")

    ## Product Unis vs Orders - Scaling
    _cases = cases["products-units-orders_scaling"] = []
    # many rare units
    _cases.append("many_rare -x 10 -y 10 -r 5 -s 16 -p 4 -P 64 -u 64 -o 8 -R -H --oap")

    # many orders
    _cases.append("many_orders -x 10 -y 10 -r 5 -s 16 -p 4 -P 4 -u 32 -o 32 -R -H --oap")

    # many orders + many rare units
    _cases.append("many_both -x 10 -y 10 -r 5 -s 16 -p 4 -P 64 -u 64 -o 32 -R -H --oap")


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
