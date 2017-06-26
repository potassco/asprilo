#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Instance generator'''

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

VERSION = "0.1"

class InstanceGenerator(object):

    def __init__(self, args):

        self._args = args

        #check if all arguments are valid
        if self._args.grid_x and self._args.grid_x < 0:
            raise ValueError("invalid grid size")
        if self._args.grid_y and self._args.grid_y < 0:
            raise ValueError("invalid grid size")
        if self._args.nodes  and self._args.nodes < 0:
            raise ValueError("invalid grid size")
        if self._args.robots and self._args.robots < 0:
            raise ValueError("invalid number of robots")
        if self._args.shelves and self._args.shelves < 0:
            raise ValueError("invalid number of shelves")
        if self._args.picking_stations  and self._args.picking_stations < 0:
            raise ValueError("invalid number of stations")
        if self._args.products and self._args.products < 0:
            raise ValueError("invalid number of product kinds")
        if self._args.product_units_total  and self._args.product_units_total < 0:
            raise ValueError("invalid number of products")
        if self._args.orders and self._args.orders < 0:
            raise ValueError("invalid number of requests")
        if self._args.num and self._args.num < 0:
            raise ValueError("invalid number of instances")
        if self._args.products and self._args.product_units_total:
            if self._args.products > self._args.product_units_total:
                raise ValueError("product_units_total must be smaller or equal to products")
        if self._args.threads > 1 and self._args.split:
            raise ValueError(
                '''only single threaded execution (-t 1) possible when splitting up (--split)
                instances''')

        self._control = None
        self._solve_opts = ["-t {0}".format(self._args.threads),
                            "--project",
                            # "--opt-mode=optN",
                            "-n {0}".format(self._args.num)]
        self._inits = None
        self._object_counters = {}
        self._instance_count = 0
        self.dest_dirs = []

        if self._args.cluster_x is None:
            self._cluster_x = int((self._args.grid_x - 2 + 0.5) / 2)
        else:
            self._cluster_x = self._args.cluster_x
        if self._args.cluster_y is None:
            self._cluster_y = int((self._args.grid_y - 4 + 0.5) / 2)
        else:
            self._cluster_y = self._args.cluster_y

    def on_model(self, m):
        self._instance_count += 1
        self._inits = []
        if self._args.console:
            print "\n"
        if self._args.console and not self._args.quiet:
            print str(self._instance_count) + ". instance:"
        atoms_list = m.symbols(terms=True)
        if self._args.debug:
            print '******DEBUG MODE: Found Model:'
            for atm in m.symbols(atoms=True):
                print atm
        for atm in [atm for atm in atoms_list if atm.name == "init"]:
            self._inits.append(atm)
        self._update_object_counter(atoms_list)
        print self._object_counters
        self.save()

    def _update_object_counter(self, atoms_list):
        '''Count objects in atom list.'''
        self._object_counters = {"x" : 0, "y" : 0, "node" : 0, "robot" : 0, "shelf" : 0,
                                 "pickingStation" : 0, "product" : 0, "order" : 0, "units" : 0}
        objects = []
        for atm in [atm for atm in atoms_list if atm.name == "init"]:
            args = atm.arguments
            if len(args) == 2 and args[0].name == "object":
                obj = args[0]
                object_name = obj.arguments[0].name
                if obj not in objects:
                    objects.append(obj)
                    if object_name not in self._object_counters:
                        self._object_counters[object_name] = 1
                    else:
                        self._object_counters[object_name] += 1
                    if args[1].name == "value" and len(args[1].arguments) == 2:
                        value_type = args[1].arguments[0].name
                        value_value = args[1].arguments[1]
                        if object_name == "node" and value_type == "at":
                            self._object_counters["x"] = max(self._object_counters["x"],
                                                             value_value.arguments[0].number)
                            self._object_counters["y"] = max(self._object_counters["y"],
                                                             value_value.arguments[1].number)
                if (object_name == "product" and args[1].name == "value" and
                        len(args[1].arguments) == 2):
                    value_type = args[1].arguments[0].name
                    value_value = args[1].arguments[1]
                    if value_type == "on" and len(value_value.arguments) == 2:
                        self._object_counters["units"] = (self._object_counters["units"] +
                                                          value_value.arguments[1].number)

    def solve(self):
        # if not self._args.quiet:
        #     print "Used args for solving: " + str(self._args)

        self._control = clingo.Control(self._solve_opts)
        self._control.load("ig.lp")
        for template in self._args.template:
            self._control.load(template)
            self._control.ground([("base", [])])
            self._control.ground([("template_stub", [])])

        if not self._args.quiet:
            print "ground..."

        # nodes
        if not (self._args.grid_x is None or self._args.grid_y is None):
            if self._args.nodes is None:
                self._control.ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                                 self._args.grid_x * self._args.grid_y])])
            else:
                self._control.ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                                 self._args.nodes])])
        # object IDs
        if self._args.robots:
            self._control.ground([("robots", [self._args.robots, self._args.robots])])
        if self._args.shelves:
            self._control.ground([("shelves", [self._args.shelves, self._args.shelves])])
        if self._args.picking_stations:
            self._control.ground([("picking_stations",
                                   [self._args.picking_stations, self._args.picking_stations])])
        if self._args.products:
            self._control.ground([("products", [self._args.products, self._args.products])])
        if self._args.orders:
            self._control.ground([("orders", [self._args.orders])])

        # layouts
        if self._args.beltway_layout:
            self._control.ground([("beltway_layout", [self._cluster_x, self._cluster_y])])
        else:
            self._control.ground([("random_layout", [])])

        # object inits
        self._control.ground([("robots_init", [])])
        self._control.ground([("shelves_init", [])])
        self._control.ground([("picking_stations_init", [])])
        if self._args.product_units_total:
            self._control.ground([("product_units", [self._args.product_units_total,
                                                     self._args.product_units_total,
                                                     self._args.product_units_per_product_shelf])])
        self._control.ground([("orders_init", [self._args.order_min_lines, self._args.order_max_lines])])

        #layouts cont;
        # TODO: simplify grounding order of layouts, constraints, object inits program parts
        # - use init/2 instead of poss/2 in layout constraints above
        if self._args.reachable_layout:
            self._control.ground([("reachable_layout", [])])


        # order constraints & optimizations
        if self._args.order_all_products:
            self._control.ground([("order_all_products", [])])
        # self._control.ground([("orders_different", [])])

        # general rules
        self._control.ground([("base", [])])

        # projection to subsets of init/2
        if self._args.prj_orders:
            self._control.ground([("project_orders", [])])
        elif self._args.prj_warehouse:
            self._control.ground([("project_warehouse", [])])
        else:
            self._control.ground([("project_all", [])])

        if not self._args.quiet:
            print "solve..."

        # solve_future = self._control.solve_async(self.on_model)
        # solve_future.wait(self._args.wait)
        # solve_future.cancel()
        # solve_result = solve_future.get()

        solve_result = self._control.solve(on_model=self.on_model)

        if not self._args.quiet:
            print "Parallel mode: " + str(self._control.configuration.solve.parallel_mode)
            print "Generated instances: " + str(self._instance_count)
            print "Solve result: " + str(solve_result)
            print "Search finished: " + str(not solve_result.interrupted)
            print "Search space exhausted: " + str(solve_result.exhausted)


    def save(self):
        self._inits.sort()
        file_name = ''
        if not self._args.console:
            if self._args.instance_count:
                instance_count = self._args.instance_count
            else:
                instance_count = self._instance_count
            local_name = (self._args.name_prefix +
                          "_".join(["x" + str(self._object_counters["x"]),
                                    "y" + str(self._object_counters["y"]),
                                    "n" + str(self._object_counters["node"]),
                                    "r" + str(self._object_counters["robot"]),
                                    "s" + str(self._object_counters["shelf"]),
                                    "ps" + str(self._object_counters["pickingStation"]),
                                    "pr" + str(self._object_counters["product"]),
                                    "u" + str(self._object_counters["units"]),
                                    "o" + str(self._object_counters["order"]),
                                    "N" + str(instance_count)]))
            if self._args.instance_dir:
                dir_suffix = local_name
            else:
                dir_suffix = ''
            if self._args.instance_dir_suffix:
                dir_suffix += self._args.instance_dir_suffix
            dest_dir = self._args.directory + dir_suffix
            self.dest_dirs.append(dest_dir)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            file_name = (dest_dir + "/" + local_name + ".lp")
        else:
            file_name = "/dev/stdout"
        ofile = open(file_name, "w")
        try:
            #head
            ofile.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            ofile.write("\n% Grid Size X:                      " + str(self._object_counters["x"]))
            ofile.write("\n% Grid Size Y:                      " + str(self._object_counters["y"]))
            ofile.write("\n% Number of Nodes:                  " + str(self._object_counters["node"]))
            ofile.write("\n% Number of Robots:                 " + str(self._object_counters["robot"]))
            ofile.write("\n% Number of Shelves:                " + str(self._object_counters["shelf"]))
            ofile.write("\n% Number of picking stations:       " + str(self._object_counters["pickingStation"]))
            ofile.write("\n% Number of products:               " + str(self._object_counters["product"]))
            ofile.write("\n% Number of product units in total: " + str(self._object_counters["units"]))
            ofile.write("\n% Number of orders:                 " + str(self._object_counters["order"]))
            ofile.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

            #body
            ofile.write("#program base.\n\n")
            # if not (self._args.grid_x is None or self._args.grid_y is None):
            #     ofile.write("timelimit("+ str(int(self._args.grid_x * self._args.grid_y * 1.5))
            #                 + ").\n\n")

            ofile.write("% init\n")
            for obj in self._inits:
                ofile.write(str(obj) + ".\n")

        except IOError:
            ofile.close()
            return
        ofile.close()
        return

    def interrupt(self):
        '''Kill all solve call threads.'''
        self._control.interrupt()


class InterruptThread(threading.Thread):
    '''Thread to interrupt solver.'''
    def __init__(self, control, timeout):
        threading.Thread.__init__(self)
        self.control = control
        self.timeout = timeout

    def run(self):
        time.sleep(self.timeout)
        self.control.interrupt()
        print '\n! Solve call timed out. All solve threads killed. \n'


class Runner(object):
    '''Runs InstanceGenerator once or multiple times.'''

    def __init__(self):
        self._cl_parser, self._cl_args = self.parse_cl_args()
        if self._cl_args.split:
            self.split_up_instances()
        else:
            self.run_once()

    def parse_cl_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-x", "--grid-x", type=int, help="the grid size in x-direction")
        parser.add_argument("-y", "--grid-y", type=int, help="the grid size in y-direction")
        parser.add_argument("-n", "--nodes", type=int, help="the number of nodes")
        parser.add_argument("-r", "--robots", type=int, help="the number of robots")
        parser.add_argument("-s", "--shelves", type=int, help="the number of shelves")
        parser.add_argument("-p", "--picking-stations", type=int,
                            help="the number of picking stations")
        parser.add_argument("-u", "--product-units-total", type=int,
                            help="the total number of product units stored in the warehouse")
        parser.add_argument("-N", "--num", type=int, default=1,
                            help="the number of instances to create")
        parser.add_argument("-C", "--console",
                            help="prints the instances to the console", action="store_true")
        parser.add_argument("-q", "--quiet",
                            help="prints nothing to the console", action="store_true")
        parser.add_argument("-d", "--directory", type=str, default="generatedInstances",
                            help="the directory to safe the files")
        parser.add_argument("--instance-dir", action="store_true",
                            help='''each instance is stored in unique directory where the
                            path is the concatenation of \'<DIRECTORY> <INSTANCE-NAME>/\'''')
        parser.add_argument("--instance-dir-suffix", type=str, default='',
                            help='''additional instance dir suffix, i.e., each instance is
                            stored in unique directory where the path is the concatenation of
                            \'<DIRECTORY> <INSTANCE-NAME> <SUFFIX>\'''')
        parser.add_argument("--instance-count", type=str,
                            help='''each instance gets the given value as running number instead
                            of using its rank in the enumeration of clasp.''')
        parser.add_argument("-f", "--name-prefix", type=str, default="",
                            help="the name prefix that eyery file name will contain")
        parser.add_argument("-v", "--version",
                            help="show the current version", action="version",
                            version=VERSION)
        parser.add_argument("-t", "--threads", type=int, default=1,
                            help="run clingo with THREADS threads")
        parser.add_argument("-w", "--wait", type=int, default=300,
                            help='''time to wait in seconds before
                            solving is aborted if not finished yet''')
        parser.add_argument("-D", "--debug", action="store_true",
                            help='''Debug output.''')

        product_args = parser.add_argument_group('product constraints')
        product_args.add_argument("-P", "--products", type=int, help="the number of product kinds")
        product_args.add_argument("--Pus", "--product-units-per-product-shelf", type=int,
                                  default=20, help="the number of each product's units per shelf",
                                  dest="product_units_per_product_shelf")

        order_args = parser.add_argument_group('order constraints')
        order_args.add_argument("-o", "--orders", type=int, help="the number of orders")
        order_args.add_argument("--olmin", "--order-min-lines", type=int, default=1,
                                help="Specifies minimum of lines per order.",
                                dest="order_min_lines")
        order_args.add_argument("--olmax", "--order-max-lines", type=int, default=1,
                                help="Specifies maximum of lines per order.",
                                dest="order_max_lines")
        order_args.add_argument("--oap", "--order-all-products", action="store_true",
                                help="Each product should at least be ordered once.",
                                dest="order_all_products")

        layout_args = parser.add_argument_group('layout constraints')
        layout_args.add_argument("-R", "--reachable-layout",
                                 help="""all shelves are reachable from all picking
                                 stations w/o moving other shelves""",
                                 action="store_true")
        layout_args.add_argument("-B", "--beltway-layout", action="store_true",
                                 help="""a beltway in form of highway
                                 nodes along the edges of the warehouse""")
        layout_args.add_argument("-X", "--cluster-x", type=int, default=2,
                                 help="the size of one rectangular shelf cluster in x-direction")
        layout_args.add_argument("-Y", "--cluster-y", type=int, default=2,
                                 help="the size of one rectangular shelf cluster in y-direction")
        project_args = parser.add_argument_group('projection and template options')
        project_args.add_argument("-T", "--template", nargs='*', type=str, default=[],
                                  help="""every created instance will contain all atoms
                                  of the template(s) (defined in #program base)""")
        project_args.add_argument("--prj-orders", action="store_true",
                                  help='project enumeration to order-related init/2 atoms')
        project_args.add_argument("--prj-warehouse", action="store_true",
                                  help='project enumeration to warehouse-related init/2 atoms')
        project_args.add_argument("--split", nargs=2, action='store', type=int,
                                  help='''splits instances into warehouse and order-related facts;
                                  takes as arguments 1.) the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.''')
        return parser, parser.parse_args()

    def run_once(self):
        sig_handled = [False] # Outter flag to indicate sig handler usage

        class TimeoutError(Exception):
            pass

        def sig_handler(signum, frame):
            sig_handled[0] = True
            if signum == signal.SIGINT:
                print '\n! Received Keyboard Interruption (Ctrl-C).\n '
                raise KeyboardInterrupt
            elif signum == signal.SIGALRM:
                print '\n! Solve call timed out!\n'
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
                print type(exc).__name__ + ":\n" + str(exc)
        finally:
            igen.interrupt()

    def split_up_instances(self):
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
    runner = Runner()

if __name__ == '__main__':
    sys.exit(main())
