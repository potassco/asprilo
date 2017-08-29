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
import clingo

# Add generator module path to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from generator.generator import InstanceGenerator

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
        self._cl_parser, self._cl_args = self.parse_cl_args()
        self._check_related_cl_args()
        if self._cl_args.split:
            self.split_up_instances()
        else:
            self.run_once()

    def parse_cl_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-x", "--grid-x", type=Control.check_positive,
                            help="the grid size in x-direction")
        parser.add_argument("-y", "--grid-y", type=Control.check_positive,
                            help="the grid size in y-direction")
        parser.add_argument("-n", "--nodes", type=Control.check_positive,
                            help="the number of nodes")
        parser.add_argument("-r", "--robots", type=Control.check_positive,
                            help="the number of robots")
        parser.add_argument("-s", "--shelves", type=Control.check_positive,
                            help="the number of shelves")
        parser.add_argument("--sc", "--shelf-coverage", type=Control.check_positive,
                            help="""the percentage of storage nodes covered by shelves; storage
                            nodes are those nodes that are not a highway node nor occupied by a
                            robot or station""",
                            dest='shelf_coverage')
        parser.add_argument("-p", "--picking-stations", type=Control.check_positive,
                            help="the number of picking stations")
        parser.add_argument("-u", "--product-units-total", type=Control.check_positive,
                            help="the total number of product units stored in the warehouse")
        parser.add_argument("-N", "--num", type=Control.check_positive, default=1,
                            help="the number of instances to create")
        parser.add_argument("-C", "--console",
                            help="prints the instances to the console", action="store_true")
        parser.add_argument("-q", "--quiet",
                            help="prints nothing to the console", action="store_true")
        parser.add_argument("-d", "--directory", type=str, default="generatedInstances",
                            help="the directory to safe the files")
        parser.add_argument("--instance-dir", action="store_true",
                            help="""each instance is stored in unique directory where the
                            path is the concatenation of \'<DIRECTORY> <INSTANCE-NAME>/\'""")
        parser.add_argument("--instance-dir-suffix", type=str, default='',
                            help="""additional instance dir suffix, i.e., each instance is
                            stored in unique directory where the path is the concatenation of
                            \'<DIRECTORY> <INSTANCE-NAME> <SUFFIX>\'""")
        parser.add_argument("--instance-count", type=str,
                            help="""each instance gets the given value as running number instead
                            of using its rank in the enumeration of clasp""")
        parser.add_argument("-f", "--name-prefix", type=str, default="",
                            help="the name prefix that eyery file name will contain")
        parser.add_argument("-v", "--version", help="show the current version", action="version",
                            version=VERSION)
        parser.add_argument("-t", "--threads", type=Control.check_positive, default=1,
                            help="run clingo with THREADS threads")
        parser.add_argument("-w", "--wait", type=Control.check_positive, default=300,
                            help="""time to wait in seconds before
                            solving is aborted if not finished yet""")
        parser.add_argument("-D", "--debug", action="store_true", help="debug output")

        product_args = parser.add_argument_group('product constraints')
        product_args.add_argument("-P", "--products", type=Control.check_positive,
                                  help="the number of product kinds")
        product_args.add_argument("--Pus", "--product-units-per-product-shelf",
                                  type=Control.check_positive, default=20,
                                  help="the number of each product's units per shelf",
                                  dest="product_units_per_product_shelf")

        order_args = parser.add_argument_group('order constraints')
        order_args.add_argument("-o", "--orders", type=Control.check_positive,
                                help="the number of orders")
        order_args.add_argument("--olmin", "--order-min-lines", type=Control.check_positive,
                                default=1,
                                help="Specifies minimum of lines per order.",
                                dest="order_min_lines")
        order_args.add_argument("--olmax", "--order-max-lines", type=Control.check_positive,
                                default=1,
                                help="Specifies maximum of lines per order.",
                                dest="order_max_lines")
        order_args.add_argument("--oap", "--order-all-products", action="store_true",
                                help="Each product should at least be ordered once.",
                                dest="order_all_products")

        layout_args = parser.add_argument_group('layout constraints')
        layout_args.add_argument("-R", "--reachable-layout",
                                 help="""all shelves are reachable from all picking stations
                                 w/o moving other shelves""", action="store_true")
        layout_args.add_argument("-H", "--highway-layout", action="store_true",
                                 help="Manhattan-style street grid using highway-nodes")
        layout_args.add_argument("-X", "--cluster-x", type=Control.check_positive, default=2,
                                 help="the size of one rectangular shelf cluster in x-direction")
        layout_args.add_argument("-Y", "--cluster-y", type=Control.check_positive, default=2,
                                 help="the size of one rectangular shelf cluster in y-direction")
        project_args = parser.add_argument_group('projection and template options')
        project_args.add_argument("-T", "--template", nargs='*', type=str, default=[],
                                  help="""every created instance will contain all atoms of the
                                  template(s) (defined in #program base)""")
        project_args.add_argument("--prj-orders", action="store_true",
                                  help='project enumeration to order-related init/2 atoms')
        project_args.add_argument("--prj-warehouse", action="store_true",
                                  help='project enumeration to warehouse-related init/2 atoms')
        project_args.add_argument("--split", nargs=2, action='store', type=Control.check_positive,
                                  help="""splits instances into warehouse and order-related facts;
                                  takes as arguments 1.) the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.""")
        return parser, parser.parse_args()


    @staticmethod
    def check_positive(value):
        """Positive int check for argparse."""
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("%s is not a positive int value!" % value)
        return ivalue

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

    def run_once(self):
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

    def split_up_instances(self):
        """Execution with split instances."""
        num_wh_inst, num_order_inst = self._cl_args.split
        parser = argparse.ArgumentParser()
        cl_args_bak = copy.deepcopy(vars(self._cl_args))

        # warehouse instances
        self._cl_parser.parse_args(args=['-d', self._cl_args.directory + '/warehouse_',
                                         '--instance-dir',
                                         '--prj-warehouse',
                                         '-N', str(num_wh_inst)],
                                   namespace=self._cl_args)
        if not self._cl_args.quiet:
                print "Creating **warehouses** using solve args: " + str(self._cl_args)
        dest_dirs=self.run_once()

        #orders instances and merge
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
            self.run_once()

            # merge
            for oinst in xrange(1, len(glob.glob(dest_dirs[winst-1] + '/orders/*.lp')) + 1):
                cl_args = vars(self._cl_args)
                cl_args.clear()
                cl_args.update(copy.deepcopy(cl_args_bak))
                path_to_order_file = glob.glob(dest_dirs[winst-1] + '/orders/*N{0}.lp'.format(oinst))[0]
                self._cl_parser.parse_args(
                    args=['-d', dest_dirs[winst-1] + '/merged',
                          '-T', path_to_warehouse_file, path_to_order_file,
                          '--instance-count', str(oinst),
                          '-N', '1'],
                    namespace=self._cl_args)
                if not self._cl_args.quiet:
                    print "Creating **merged instances** using solve args: " + str(self._cl_args)
                self.run_once()

def main():
    Control()

if __name__ == '__main__':
    sys.exit(main())
