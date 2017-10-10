#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test instance generator'''
import subprocess
import sys
import os
import shlex
import argparse
from collections import OrderedDict
from glob import glob
from cases import define_cases, general_pars

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
        template_pars = ''
        for subcat, subcases in _cases.items():
            for case in subcases:
                case_dir = subcat
                case_pars = case['pars']
                # if 'template' in case: # Adjust dest dir for templates
                #     case_dir += '/templates'
                # else:
                #     case_dir += '/instances'
                dest_pre = '{directory}/{cat}/{case_dir}'.format(directory=args.directory,
                                                                 cat=cat,
                                                                 case_dir=case_dir)
                dest = dest_pre
                command_common = shlex.split(
                    '''python ../ig
                    -V
                    -t {threads}
                    -w {wait}
                    {case_pars}'''.format(threads=args.threads,
                                          wait=args.wait,
                                          case_pars=case_pars))

                if 'template' in case: # Generate templates
                    template_pars = case_pars
                    if args.split:
                        models = args.split[0]
                    else:
                        models = args.models
                    dest += '/templates'
                    command = list(command_common)
                    command.extend(shlex.split(
                        '''
                        -N {models}
                        -d {dest}
                        '''.format(models=models, dest=dest)))
                    print '*** Running TEMPLATE Command:'
                    run_command(command, dest, True)
                else: # Generate instances either
                    templates = sorted(glob(r'{dest_pre}/templates/*.lp'.format(dest_pre=dest_pre)))
                    if templates: # ... with a template; or
                        if args.split:
                            split = '--split 1 {}'.format(args.split[1])
                        for idx, temp in enumerate(templates):
                            dest = '{dest_pre}/instances_T{idx}'.format(dest_pre=dest_pre,
                                                                        idx=str(idx+1))
                            command = list(command_common)
                            command.extend(shlex.split(template_pars))
                            command.extend(shlex.split(
                                '''
                                -N {models}
                                {split}
                                -T {template}
                                -d {dest}
                                '''.format(models=args.models,
                                           split=split,
                                           template=temp,
                                           dest=dest)))
                            print '*** Running COMBINED Command:'
                            run_command(command, dest)
                    else: # ... regular, i.e., w/o template
                        command = list(command_common)
                        command.extend(shlex.split(
                            '''
                            -N {models}
                            {split}
                            '''.format(models=args.models, split=split)))
                        print '*** Running REGULAR Command:'
                        run_command(command, dest)

def run_command(command, dest, check_exists=False):
    if check_exists and os.path.isdir(dest):
        print '\n**** ' + dest + ' exists, skipping! *****\n'
        return
    else:
        command.extend(shlex.split(general_pars))
        print str(command)
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
    gen_instances(define_cases(args.directory), args)

sys.exit(main())
