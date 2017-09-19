#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General Execution Control."""
from __future__ import absolute_import
import argparse
import logging
import copy
import glob
import signal
from collections import OrderedDict
import yaml

from generator.generator import InstanceGenerator
from generator.utils.aux import check_positive, SmartFormatter
from generator.utils.logger import setup_logger
from generator import release

LOG = logging.getLogger('custom')

class Control(object):
    """Runs InstanceGenerator once or multiple times."""
    def __init__(self, args=None):
        self._cl_parser, self._args = Control._parse_cl_args(args)
        self._check_related_cl_args()
        setup_logger(self._args.loglevel)

    def run(self):
        """Main method to dispatch instance generation."""
        if self._args.batch:
            self._run_batch()
        else:
            self._run_once()

    def _run_once(self):
        """Regular single instance generation."""
        # self._cl_parser, self._args = Control._parse_cl_args()
        if self._args.split:
            self._gen_split()
        else:
            self._gen()

    def _run_batch(self):
        """Runs batch_file job of instance generations."""
        LOG.info("Running in batch mode")
        try:
            with open(self._args.batch, 'r') as batch_file:
                invocations, global_settings = self._extract_invocations(batch_file.read(),
                                                                         self._args.directory)
                for invoc in invocations:
                    invoc.extend(global_settings)
                    try:
                        LOG.info("Running invocation for pars: %s ", str(invoc))
                        Control(invoc).run()
                    except Exception, exc:
                        LOG.error("""During batch mode, received exception %s while running with
                        parameters %s""", exc, str(invoc))
        except IOError as err:
            LOG.error("IOError while trying to open batch file \'%s\': %s", self._args.batch, err)

    def _carry_over_args(self):
        """In batch mode, carries over relevant args."""
        pass

    def _extract_invocations(self, batch, parent_path='.'):
        """Returns the required invocations from a batch job specification.

        :param str batch: a batch job specification.
        :returns: a list of list of command line parameters representing the list of single instance
                  generation tasks to process
        :rtype: list of lists of strings

        """
        def odict_constructor(loader, node):
            """OrderedDict constructor for yaml parser."""
            return OrderedDict(loader.construct_pairs(node))

        yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, odict_constructor)
        content = yaml.load(batch)
        LOG.debug("Content parsed from YAML batch file: %s", str(content))
        invocations = []
        global_settings = []
        path = []
        stack = [content.iteritems()]
        visit_next = None
        prev_leaf = False
        while stack or visit_next:
            LOG.debug("Current path: %s", str(path))
            if visit_next:
                itr = visit_next
            else:
                itr = stack.pop()
                if path and not prev_leaf:
                    popped = path.pop()
                    LOG.debug("Popped from path:  %s", str(popped))
            try:
                key, val = itr.next()
            except StopIteration:
                if path and prev_leaf:
                    LOG.debug("Last leaf path: %s", str(path))
                    if path[0] == 'global_settings':
                        global_settings.extend(Control._convert_path_to_args(path,
                                                                             parent_path,
                                                                             True))
                    else:
                        invocations.append(Control._convert_path_to_args(path, parent_path))
                    popped = path.pop()
                    LOG.debug("Popped from path:  %s", str(popped))
                    prev_leaf = False
            else:
                stack.append(itr)
                LOG.debug("Visiting: %s | %s", str(key), str(val))
                if isinstance(val, OrderedDict):
                    path.append(key)
                    visit_next = val.iteritems()
                    prev_leaf = False
                elif key:
                    LOG.debug("Leaf detected: %s :: %s", str(key), str(val))
                    if isinstance(path[-1], list):
                        path[-1].append((key, val))
                    else:
                        path.append([(key, val)])
                    visit_next = None
                    prev_leaf = True
            key = val = None
        LOG.debug("Invocations: %s", str(invocations))
        return invocations, global_settings
    
    @staticmethod
    def _convert_path_to_args(path, parent_path='.', leafs_only=False):
        """Converts path to list of input args for _parse_cl_args."""
        args = ['-d', parent_path]
        for part in path:
            if isinstance(part, list): #Leaf level
                leaf_args = []
                for tup in part:
                    leaf_args += [str(elm) for elm in tup if elm is not True]
                if leafs_only:
                    args = leaf_args
                    break
                else:
                    args.extend(leaf_args)
            else:
                args[1] = os.path.join(args[1], str(part))
        return args

    def _gen(self):
        """Regular instance generation."""
        sig_handled = [False] # Outter flag to indicate sig handler usage

        class TimeoutError(Exception):
            pass

        def sig_handler(signum, frame):
            sig_handled[0] = True
            if signum == signal.SIGINT:
                LOG.warn("\n! Received Keyboard Interruption (Ctrl-C).\n")
                raise KeyboardInterrupt
            elif signum == signal.SIGALRM:
                LOG.warn("\n! Solve call timed out!\n")
                raise TimeoutError()

        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGALRM, sig_handler)
        igen = InstanceGenerator(self._args)
        try:
            signal.alarm(self._args.wait)
            igen.solve()
            return igen.dest_dirs
        except Exception as exc:
            if sig_handled[0]:
                pass
            else:
                LOG.error("%s: %s", type(exc).__name__, exc)
        finally:
            igen.interrupt()

    def _gen_split(self):
        """Execution with split up instances."""
        num_wh_inst, num_order_inst = self._args.split
        argparse.ArgumentParser()
        cl_args_bak = copy.deepcopy(vars(self._args))

        # warehouse instances
        self._cl_parser.parse_args(args=['-d', self._args.directory + '/warehouse_',
                                         '--instance-dir',
                                         '--prj-warehouse',
                                         '-N', str(num_wh_inst)],
                                   namespace=self._args)

        LOG.info("Creating **warehouses** using solve args: %s", str(self._args))
        dest_dirs = self._gen()

        # orders instances and merge
        for winst in xrange(1, num_wh_inst+1):

            # orders only
            _cl_args = vars(self._args)
            _cl_args.clear()
            _cl_args.update(copy.deepcopy(cl_args_bak))
            _cl_args['oap'] = False
            path_to_warehouse_file = glob.glob(dest_dirs[winst-1] + '/*.lp')[0]
            self._cl_parser.parse_args(
                args=['-d', dest_dirs[winst-1],
                      '--instance-dir-suffix', '/orders',
                      '-T', path_to_warehouse_file,
                      '--prj-orders',
                      '-N', str(num_order_inst)],
                namespace=self._args)

            LOG.info("Creating **orders** using solve args: %s", str(self._args))
            self._gen()

            # merge
            for oinst in xrange(1, len(glob.glob(dest_dirs[winst-1] + '/orders/*.lp')) + 1):
                _cl_args = vars(self._args)
                _cl_args.clear()
                _cl_args.update(copy.deepcopy(cl_args_bak))
                path_to_order_file = glob.glob(dest_dirs[winst-1] +
                                               '/orders/*N{0}.lp'.format(oinst))[0]
                self._cl_parser.parse_args(
                    args=['-d', dest_dirs[winst-1] + '/merged',
                          '-T', path_to_warehouse_file, path_to_order_file,
                          '--instance-count', str(oinst),
                          '-N', '1'],
                    namespace=self._args)
                LOG.info("Creating **merged instances** using solve args: %s", str(self._args))
                self._gen()

    def _check_related_cl_args(self):
        """Checks consistency wrt. related command line args."""
        if self._args.shelves and self._args.shelf_coverage:
            raise ValueError("""Number of shelves specified by both quantity (-s) and
            coverage rate (--sc)""")
        if self._args.products and self._args.product_units_total:
            if self._args.products > self._args.product_units_total:
                raise ValueError("Product_units_total must be smaller or equal to products")
        if self._args.threads > 1 and self._args.split:
            raise ValueError("""Only single threaded execution (-t 1) possible when splitting
            up (--split) instances""")

    @staticmethod
    def _parse_cl_args(args=None):
        """Argument parsing method.

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
        basic_args.add_argument('-v', '--version', action='version',
                                version='%(prog)s {0}'.format(release.__version__))
        basic_args.add_argument("-t", "--threads", type=check_positive, default=1,
                                help="run clingo with THREADS threads")
        basic_args.add_argument("-w", "--wait", type=check_positive, default=300,
                                help="""time to wait in seconds before
                                 solving is aborted if not finished yet""")
        basic_args.add_argument('-V', '--verbose', action='store_const', dest='loglevel',
                                const=logging.INFO, default=logging.WARNING,
                                help='Verbose output.')
        basic_args.add_argument('-D', '--debug', action='store_const', dest='loglevel',
                                const=logging.DEBUG, default=logging.WARNING,
                                help='Debug output.')
        basic_args.add_argument("-J", "--batch", type=str, metavar="JOB",
                                help="""a batch_file job of multiple instance generations specified
                                by a job file; takes as additional options only directory (-d), 
                                debug (-D) or verbose (-V) flag into account, otherwise ignored""")

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
                                  help="""every created instance will contain all atoms
                                  defined in #program base of the template file(s)""")
        project_args.add_argument("--prj-orders", action="store_true",
                                  help='project enumeration to order-related init/2 atoms')
        project_args.add_argument("--prj-warehouse", action="store_true",
                                  help='project enumeration to warehouse-related init/2 atoms')
        project_args.add_argument("--split", nargs=2, action='store', type=check_positive,
                                  metavar="NUM",
                                  help="""splits instances into warehouse and order-related facts;
                                  takes as arguments 1.) the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.""")
        return parser, parser.parse_args(args)
