#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instance Generator Script."""

import sys
import os
import random
import time
import argparse
from math import fabs
import copy
import glob
import threading, time
import signal
import json
import clingo

# Add generator module path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from generator.generator import InstanceGenerator
from generator.aux import check_positive, SmartFormatter

VERSION = "0.1"

class InterruptThread(threading.Thread):
    """Thread to interrupt solver."""
    def __init__(self, prg, timeout):
        threading.Thread.__init__(self)
        self._prg = prg
        self.timeout = timeout

    def run(self):
        time.sleep(self.timeout)
        self._prg.interrupt()
        print '\n! Solve call timed out. All solve threads killed. \n'


class Control(object):
    """Runs InstanceGenerator once or multiple times."""

    def __init__(self):
        self._cl_parser, self._cl_args = self._parse_cl_args() #TODO: lift arg parsing to main, pass as argument
        self._check_related_cl_args()
        if self._cl_args.split:
            self._run_split()
        else:
            self._run()

    def _parse_cl_args(self, args=None): # TODO: lift to pure function to be called by main()
        """Argument paring method.

        Parses command line arguments by default or, alternatively, an optional list of arguments
        passed by parameter.

        :type list: A list of argument strings or None.

        """
        parser = argparse.ArgumentParser(prog='ig',
                                         formatter_class=SmartFormatter,
                                         add_help=False)
        basic_args = parser.add_argument_group("Basic options")
        basic_args.add_argument("-h", "--help", action="help",
                                help="Show this help message and exit")
        basic_args.add_argument("-x", "--grid-x", type=check_positive,
                                help="the grid size in x-direction")
        basic_args.add_argument("-y", "--grid-y", type=check_positive,
                                help="the grid size in y-direction")
        basic_args.add_argument("-n", "--nodes", type=check_positive,
                                help="the number of nodes")
        basic_args.add_argument("-r", "--robots", type=check_positive,
                                help="the number of robots")
        basic_args.add_argument("-s", "--shelves", type=check_positive,
                                help="the number of shelves")
        basic_args.add_argument("--sc", "--shelf-coverage", type=check_positive,
                                help="""the percentage of storage nodes covered by shelves; storage
                                nodes are those nodes that are not a highway node nor occupied by a
                                robot or station""",
                                dest='shelf_coverage')
        basic_args.add_argument("-p", "--picking-stations", type=check_positive,
                                help="the number of picking stations")
        basic_args.add_argument("-u", "--product-units-total", type=check_positive,
                                help="the total number of product units stored in the warehouse")
        basic_args.add_argument("-N", "--num", type=int, default=1,
                                help="the number of instances to create")
        basic_args.add_argument("-C", "--console",
                                help="prints the instances to the console", action="store_true")
        basic_args.add_argument("-q", "--quiet",
                                help="prints nothing to the console", action="store_true")
        basic_args.add_argument("-d", "--directory", type=str, default="generatedInstances",
                                help="the directory to safe the files")
        basic_args.add_argument("--instance-dir", action="store_true",
                                help="""each instance is stored in unique directory where the
                                path is the concatenation of \'<DIRECTORY> <INSTANCE-NAME>/\'""")
        basic_args.add_argument("--instance-dir-suffix", type=str, default='',
                                help="""additional instance dir suffix, i.e., each instance is
                                stored in unique directory where the path is the concatenation of
                                \'<DIRECTORY> <INSTANCE-NAME> <SUFFIX>\'""")
        basic_args.add_argument("--instance-count", type=str,
                                help="""each instance gets the given value as running number instead
                                of using its rank in the enumeration of clasp""")
        basic_args.add_argument("-f", "--name-prefix", type=str, default="",
                                help="the name prefix that eyery file name will contain")
        basic_args.add_argument("-v", "--version", help="show the current version",
                                action="version", version=VERSION)
        basic_args.add_argument("-t", "--threads", type=check_positive, default=1,
                                help="run clingo with THREADS threads")
        basic_args.add_argument("-w", "--wait", type=check_positive, default=300,
                                help="""time to wait in seconds before
                                solving is aborted if not finished yet""")
        basic_args.add_argument("-D", "--debug", action="store_true", help="debug output")

        product_args = parser.add_argument_group("Product constraints")
        product_args.add_argument("-P", "--products", type=check_positive,
                                  help="the number of product kinds")
        product_args.add_argument("--Pus", "--product-units-per-product-shelf",
                                  type=check_positive, default=20,
                                  help="the number of each product's units per shelf",
                                  dest="product_units_per_product_shelf")

        order_args = parser.add_argument_group("Order constraints")
        order_args.add_argument("-o", "--orders", type=check_positive,
                                help="the number of orders")
        order_args.add_argument("--olmin", "--order-min-lines", type=check_positive,
                                default=1,
                                help="Specifies minimum of lines per order.",
                                dest="order_min_lines")
        order_args.add_argument("--olmax", "--order-max-lines", type=check_positive,
                                default=1,
                                help="Specifies maximum of lines per order.",
                                dest="order_max_lines")
        order_args.add_argument("--oap", "--order-all-products", action="store_true",
                                help="Each product should at least be ordered once.",
                                dest="order_all_products")

        layout_args = parser.add_argument_group(
            "Layout constrains",
            """There are two major layout categories: *random* as default, or *highway* via the -H
            flag. Depending on the major layout type, there are further customization options
            available as follows.\n\n""")
        layout_ge_args = parser.add_argument_group("* General layout constraints")
        layout_ge_args.add_argument("-R", "--reachable-shelves",
                                    help="""all shelves are reachable from all picking stations
                                    w/o moving other shelves""", action="store_true")
        layout_rd_args = parser.add_argument_group("* Constraints for the *random* layout")
        layout_rd_args.add_argument("--gs", "--gap-size", type=check_positive,
                                    dest="gap_size", default=2,
                                    help="""the maximum size of "gaps" (i.e., blocked node
                                    components) in the floor grid.""")
        layout_hw_args = parser.add_argument_group("* Constraints for the *highway* layout")
        layout_hw_args.add_argument("-H", "--highway-layout", action="store_true",
                                    help="Manhattan-style street grid using highway-nodes")
        layout_hw_args.add_argument("-X", "--cluster-x", type=check_positive, default=2,
                                    help="""for highway-layout: the size of one rectangular shelf
                                    cluster in x-direction""")
        layout_hw_args.add_argument("-Y", "--cluster-y", type=check_positive, default=2,
                                    help="""for highway-layout: the size of one rectangular shelf
                                    cluster in y-direction""")
        layout_hw_args.add_argument("-B", "--beltway-width", type=check_positive, default=1,
                                    help="""for highway layout: the width of the beltway surrounding
                                    all shelf clusters""")

        project_args = parser.add_argument_group("Projection and template options")
        project_args.add_argument("-T", "--template", nargs='*', type=str, default=[],
                                  help="""every created instance will contain all atoms of the
                                  template(s) (defined in #program base)""")
        project_args.add_argument("--prj-orders", action="store_true",
                                  help='project enumeration to order-related init/2 atoms')
        project_args.add_argument("--prj-warehouse", action="store_true",
                                  help='project enumeration to warehouse-related init/2 atoms')
        project_args.add_argument("--split", nargs=2, action='store', type=check_positive,
                                  help="""splits instances into warehouse and order-related facts;
                                  takes as arguments 1.) the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.""")
        return parser, parser.parse_args(args)

    def _check_related_cl_args(self):
        """Checks consistency wrt. related command line args."""
        if self._cl_args.shelves and self._cl_args.shelf_coverage:
            raise ValueError("""Number of shelves specified by both quantity (-s) and
            coverage rate (--sc)""")
        if self._cl_args.products and self._cl_args.product_units_total:
            if self._cl_args.products > self._cl_args.product_units_total:
                raise ValueError("Product_units_total must be smaller or equal to products")
        if self._cl_args.threads > 1 and self._cl_args.split:
            raise ValueError("""Only single threaded execution (-t 1) possible when splitting
            up (--split) instances""")

    def _run(self):
        """Regular execution."""
        sig_handled = [False] # Outter flag to indicate sig handler usage

        class TimeoutError(Exception):
            pass

        def sig_handler(signum, frame):
            sig_handled[0] = True
            if signum == signal.SIGINT:
                print "\n! Received Keyboard Interruption (Ctrl-C).\n"
                raise KeyboardInterrupt
            elif signum == signal.SIGALRM:
                print "\n! Solve call timed out!\n"
                raise TimeoutError()

        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGALRM, sig_handler)
        igen = InstanceGenerator(self._cl_args)
        try:
            signal.alarm(self._cl_args.wait)
            igen.solve()
            return igen.dest_dirs
        except Exception as exc:
            if sig_handled[0]:
                pass
            else:
                print type(exc).__name__ + ':\n' + str(exc)
        finally:
            igen.interrupt()

    def _run_split(self):
        """Execution with split up instances."""
        num_wh_inst, num_order_inst = self._cl_args.split
        argparse.ArgumentParser()
        cl_args_bak = copy.deepcopy(vars(self._cl_args))

        # warehouse instances
        self._cl_parser.parse_args(args=['-d', self._cl_args.directory + '/warehouse_',
                                         '--instance-dir',
                                         '--prj-warehouse',
                                         '-N', str(num_wh_inst)],
                                   namespace=self._cl_args)
        if not self._cl_args.quiet:
            print "Creating **warehouses** using solve args: " + str(self._cl_args)
        dest_dirs = self._run()

        # orders instances and merge
        for winst in xrange(1, num_wh_inst+1):

            # orders only
            cl_args = vars(self._cl_args)
            cl_args.clear()
            cl_args.update(copy.deepcopy(cl_args_bak))
            cl_args['oap'] = False
            path_to_warehouse_file = glob.glob(dest_dirs[winst-1] + '/*.lp')[0]
            self._cl_parser.parse_args(
                args=['-d', dest_dirs[winst-1],
                      '--instance-dir-suffix', '/orders',
                      '-T', path_to_warehouse_file,
                      '--prj-orders',
                      '-N', str(num_order_inst)],
                namespace=self._cl_args)
            if not self._cl_args.quiet:
                print "Creating **orders** using solve args: " + str(self._cl_args)
            self._run()

            # merge
            for oinst in xrange(1, len(glob.glob(dest_dirs[winst-1] + '/orders/*.lp')) + 1):
                cl_args = vars(self._cl_args)
                cl_args.clear()
                cl_args.update(copy.deepcopy(cl_args_bak))
                path_to_order_file = glob.glob(dest_dirs[winst-1] +
                                               '/orders/*N{0}.lp'.format(oinst))[0]
                self._cl_parser.parse_args(
                    args=['-d', dest_dirs[winst-1] + '/merged',
                          '-T', path_to_warehouse_file, path_to_order_file,
                          '--instance-count', str(oinst),
                          '-N', '1'],
                    namespace=self._cl_args)
                if not self._cl_args.quiet:
                    print "Creating **merged instances** using solve args: " + str(self._cl_args)
                self._run()

def main():
    """Main."""
    # TODO: batch injection here
    Control()

if __name__ == '__main__':
    sys.exit(main())
