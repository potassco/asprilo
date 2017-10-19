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
from cases_workaround import define_cases, general_pars

def gen_instances(cases, args):
    if args.cats:
        cases = {cat : cases[cat] for cat in args.cats}
    if args.subcats:
        for cat in cases:
            # cases[cat] = {_cat : cases[cat][_cat] for _cat in args.subcats}
            filtered_cat = OrderedDict()
            for _cat in args.subcats:
                filtered_cat[_cat] = cases[cat][_cat]
            cases[cat] = filtered_cat
    if args.split:
        split = '--split {0} {1}'.format(args.split[0], args.split[1])
    else:
        split = ''
    for cat, _cases in cases.items():
        for subcat, subcases in _cases.items():
            template_dir = template_suffix = None
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
                    # if args.split:
                    #     models = args.split[0]
                    # else:
                    #     models = args.models
                    dest += '/templates'
                    if 'suffix' in case:
                        dest += '/' + case['suffix']
                        template_suffix = case['suffix']
                    else:
                        template_suffix = ''
                    # Add template option if template uses in turn another template
                    if  template_dir:
                        templates = sorted(glob(r'{template_dir}/*.lp'.format(
                            template_dir=template_dir)))
                        for idx, temp in enumerate(templates):
                            command = list(command_common)
                            command.extend(shlex.split(
                                '''
                                -f PrevTemp{idx}_
                                -N 1
                                -T {template}
                                -d {dest}
                                '''.format(idx=idx, models=1, template=temp, dest=dest)))
                            print '*** Running NESTED TEMPLATE Command:'
                            run_command(command, dest, False)
                    else:
                        command = list(command_common)
                        command.extend(shlex.split(
                            '''
                            -N {models}
                            -d {dest}
                            '''.format(models=args.templates, dest=dest)))
                        print '*** Running TEMPLATE Command:'
                        run_command(command, dest, True)
                    template_dir = dest
                # Otherwise, generate instances either
                else:
                    if template_dir: # ... with a template; or
                        templates = sorted(glob(r'{template_dir}/*.lp'.format(
                            template_dir=template_dir)))
                        if args.split:
                            split = '--split 1 {}'.format(args.split[1])
                        for idx, temp in enumerate(templates):
                            dest = '{dest_pre}/instances/per_template/{temp_suffix}_T{idx}'.format(
                                dest_pre=dest_pre,
                                temp_suffix=template_suffix,
                                idx=str(idx+1))
                            if 'suffix' in case:
                                dest += '/' + case['suffix']
                            command = list(command_common)
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
                        template_dir = template_suffix = None
                    else: # ... regular, i.e., w/o template
                        command = list(command_common)
                        if 'suffix' in case:
                            dest += '/' + case['suffix']
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
    parser.add_argument('-s', '--subcats', nargs='*', help='optional list of benchmark sub-categories to create')
    parser.add_argument('-d', '--directory', type=str, default='generatedInstances',
                        help="the directory to safe the files")
    parser.add_argument('-t', '--threads', type=int, help='number of clasp threads', default=1)
    parser.add_argument('-w' , '--wait', type=int,
                        help='time to wait in seconds before solving is aborted if not finished yet', default=300)
    parser.add_argument('-N', '--models', type=int, help='number of instances', default=10)
    parser.add_argument('--TN', '--templates', dest='templates', type=int, help='number of template instances', default=1)
    parser.add_argument('--split', nargs=2, type=int,
                        help='''splits instances into warehouse and
                                  order-related facts; takes as arguments 1.)
                                  the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.''')
    args = parser.parse_args()
    gen_instances(define_cases(args.directory), args)

sys.exit(main())
