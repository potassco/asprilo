#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General Execution Control."""
from __future__ import absolute_import
import os
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
    def __init__(self, args=None, parent=None):
        namespace = None
        if parent: # Carrying over settings from parent
            nsdict = {k: copy.deepcopy(v) for k, v in vars(parent.args).items()
                      if k != 'batch'}
            if parent.args.skip_existing_sub:
                nsdict['skip_existing'] = True
            namespace = argparse.Namespace(**nsdict)
        self._cl_parser, self._args = Control._parse_cl_args(args, namespace)
        self._check_related_cl_args()
        if not parent:
            setup_logger(self._args.loglevel)

    @property
    def args(self):
        """Property for command line args."""
        return self._args

    @property
    def cl_parser(self):
        """Property for command line parser."""
        return self._cl_parser

    def run(self):
        """Main method to dispatch instance generation."""
        if not self._args.batch and os.path.isdir(self._args.directory):
            if self._args.skip_existing:
                LOG.warn("Skipping, since directory \'%s\' exists!", self._args.directory)
                return
            else:
                LOG.warn('Writing in existing directory!')
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
                    if self._args.cat: # Filter selected categories
                        if not [cat for cat in self._args.cat if
                                invoc[1].startswith('{}/{}'.format(self._args.directory, cat))]:
                            LOG.warn("Categories provided, skipping mismatching invocation: %s",
                                     str(invoc))
                            continue
                    invoc.extend(global_settings)
                    try:
                        LOG.info("Running invocation for pars: %s ", str(invoc))
                        Control(invoc, self).run()
                    except Exception, exc:
                        LOG.error("""During batch mode, received exception \'%s\' while running with
                        parameters %s""", exc, str(invoc))
        except IOError as err:
            LOG.error("IOError while trying to open batch file \'%s\': %s", self._args.batch, err)


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
        invocations, global_settings = self._collect_invocs(content, None, parent_path)
        LOG.debug("Global settings: %s", str(global_settings))
        LOG.debug("Invocations: %s", str(invocations))
        #exit(1)
        return invocations, global_settings

    def _collect_invocs(self, content, path=None, parent_path='.'):
        invocations = []
        global_settings = []
        path = path or []
        warehouse_invoc = []
        LOG.debug("Current path: %s", str(path))
        if isinstance(content, OrderedDict):
            for key, val in content.items():
                if key == 'pre':
                    LOG.debug("Warehouse leaf found %s", str(val))
                    warehouse_invoc, _ = self._collect_invocs(val, path, parent_path)
                    # If po missing or --who given, add invocation directly
                    if (content.keys().index(key) is len(content) - 1 or
                            self._args.pre_only or
                            self.args.pre_too):
                        invocations.extend(warehouse_invoc)
                elif key == 'var':
                    if self._args.pre_only:
                        continue
                    else:
                        LOG.debug("Products-Orders leaf found %s", str(val))
                        invs, _ = self._collect_invocs(val, path, parent_path)
                        invocations.extend([list(*warehouse_invoc) + inv for inv in invs])
                elif isinstance(val, OrderedDict):
                    path.append(key)
                    invs, gls = self._collect_invocs(val, path, parent_path)
                    invocations.extend(invs)
                    global_settings.extend(gls)
                    if path and content.keys().index(key) is len(content) - 1:
                        path.pop()
                else: # leaf level
                    if path and isinstance(path[-1], list):
                        path[-1].append((key, val))
                    else:
                        path.append([(key, val)])
                    if content.keys().index(key) is len(content) - 1: # last leaf
                        if path and path[0] == 'global_settings':
                            global_settings.extend(self._convert_path_to_args(path, parent_path,
                                                                              True))
                            path.pop()
                        elif path and path[0] == 'var':
                            invocations.append(self._convert_path_to_args(path[1:], parent_path,
                                                                          True))
                            LOG.debug("Added the following path to invocations: %s", str(path[1:]))
                        elif path and path[0] == 'run_configs':
                            invocations.append(self._convert_path_to_args(path[1:], parent_path))
                            LOG.debug("Added the following path to invocations: %s", str(path[1:]))
                            path.pop()
                        path.pop()
        elif isinstance(content, list): #list of product-order settings
            for po_conf in content:
                invs, gls = self._collect_invocs(po_conf, ['var'], parent_path)
                invocations.extend(invs)
                global_settings.extend(gls)
        return invocations, global_settings

    def _convert_path_to_args(self, path, parent_path='.', leafs_only=False):
        """Converts path to list of input args for _parse_cl_args."""
        args = ['-d', parent_path]
        for part in path:
            if isinstance(part, list): #Leaf level
                leaf_args = []
                rel_template_path = False
                for elm in [elm for tup in part for elm in tup]:
                    if isinstance(elm, list):
                        leaf_args += [str(itm) for itm in elm]
                    elif isinstance(elm, bool):
                        if elm is False:
                            leaf_args.pop()
                        else:
                            pass
                    elif rel_template_path:
                        leaf_args += [os.path.join(parent_path, elm)]
                        rel_template_path = False
                    elif (elm == '-T' or elm == '--template') and self._args.template_relative:
                        rel_template_path = True
                        leaf_args += [str(elm)]
                    else:
                        leaf_args += [str(elm)]
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
            """Time out exception."""
            pass

        def sig_handler(signum, frame):
            """Custom signal handler."""
            sig_handled[0] = True
            if signum == signal.SIGINT:
                LOG.warn("\n! Received Keyboard Interruption (Ctrl-C).\n")
                raise KeyboardInterrupt
            elif signum == signal.SIGALRM:
                LOG.warn("Solve call timed out!")
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
    def _parse_cl_args(args=None, namespace=None):
        """Argument parsing method.

         Parses command line arguments by default or, alternatively, an optional list of arguments
         passed by parameter.

         :type args: A list of argument strings or None.
         :type namespace: An existing argparse.Namespace object to use instead of new one.

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
                                help="the number of instances to create (default: %(default)s)")
        basic_args.add_argument("-C", "--console",
                                help="prints the instances to the console", action="store_true")
        basic_args.add_argument("-d", "--directory", type=str, default="generatedInstances",
                                help="the directory to safe the files (default: %(default)s)")
        basic_args.add_argument("--se", "--skip-existing", action="store_true",
                                dest="skip_existing",
                                help="""skip instance generation if destination directory
                                already exists""")
        basic_args.add_argument("--instance-dir", action="store_true",
                                help="""each instance is stored in unique directory where the
                                 path is the concatenation of \'<DIRECTORY>/<INSTANCE-NAME>/\'""")
        basic_args.add_argument("--instance-dir-suffix", type=str, default='',
                                help="""additional instance dir suffix, i.e., each instance is
                                 stored in unique directory where the path is the concatenation of
                                 \'<DIRECTORY>/<INSTANCE-NAME><SUFFIX>/\'""")
        basic_args.add_argument("--instance-count", type=str,
                                help="""each instance gets the given value as running number instead
                                 of using its rank in the enumeration of clasp""")
        basic_args.add_argument("-f", "--name-prefix", type=str, default="",
                                help="the name prefix that eyery file name will contain")
        basic_args.add_argument('-v', '--version', action='version',
                                version='%(prog)s {0}'.format(release.__version__))
        basic_args.add_argument("-t", "--threads", type=check_positive, default=1,
                                help="run clingo with THREADS threads (default: %(default)s)")
        basic_args.add_argument("-w", "--wait", type=check_positive, default=300,
                                help="""time to wait in seconds before
                                 solving is aborted if not finished yet (default: %(default)s)""")
        basic_args.add_argument('--random', action='store_true', dest='random',
                                help="""Randomize clingo\'s model enumeration based on the flags
                                \'--rand-freq\', \'--sign-def\', and \'--seed\'""")
        basic_args.add_argument("--rand-freq", type=float, default=0.5, dest='rand_freq',
                                metavar='PERCENTAGE',
                                help="""for model randomization: the \'--rand-freq=%(metavar)s\'
                                flag passed to clingo (default: %(default)s)""")
        basic_args.add_argument("--sign-def", type=str, default='rnd', dest='sign_def',
                                metavar='DEFAULT_SIGN',
                                help="""for model randomization: the \'--sign-def=%(metavar)s\' flag
                                passed to clingo (default: %(default)s)""")
        basic_args.add_argument("--seed", type=int, default=123456789, dest='seed',
                                metavar='SEED',
                                help="""for model randomization: the \'--seed=%(metavar)s\' flag
                                passed to clingo (default: %(default)s)""")
        basic_args.add_argument('-V', '--verbose', action='store_const', dest='loglevel',
                                const=logging.INFO, default=logging.WARNING,
                                help='verbose output (default: %(default)s)')
        basic_args.add_argument('-D', '--debug', action='store_const', dest='loglevel',
                                const=logging.DEBUG, default=logging.WARNING,
                                help='debug output (default: %(default)s)')
        basic_args.add_argument("--xor", type=int, default=None,
                                help="the number of xor constraints to create")

        batch_args = parser.add_argument_group("Batch mode options")
        batch_args.add_argument("-j", "--batch", type=str, metavar="JOB",
                                help="""a batch job of multiple instance generations specified
                                by a job file; Warning: additional command line parameters will be carried over
                                as input parameters for single instance generation runs, unless explicitly
                                redefined in the job file""")
        batch_args.add_argument('-c', '--cat', nargs='*', type=str,
                                help="""optional list of names (i.e., prefixes) of sub-categories
                                to create""")
        batch_args.add_argument("--su", "--skip-existing-sub", action="store_true",
                                dest="skip_existing_sub",
                                help="""during batch instance generation, skip those sub-directories
                                that exist; helpful to resume interrupted generation jobs""")
        batch_args.add_argument('--tr', '--template-relative', action='store_true',
                                dest='template_relative',
                                help="""consider template paths relative to the destination
                                directory (-d) if given""")
        batch_args.add_argument('--preo', '--pre-only', action='store_true', dest='pre_only',
                                help="""*only* compute instances for the configuration presets
                                instead of their variants""")
        batch_args.add_argument('--pret', '--pre-too', action='store_true', dest='pre_too',
                                help="""*additionally* compute instances for the
                                configuration presets in addition to their variants""")

        product_args = parser.add_argument_group("Product constraints")
        product_args.add_argument("-P", "--products", type=check_positive,
                                  help="the number of product kinds")
        product_args.add_argument("--prs", "--products-per-shelf",
                                  type=check_positive, default=20,
                                  help="""the maximum number of products per shelf
                                  (default: %(default)s)""",
                                  dest="products_per_shelf")
        product_args.add_argument("--spr", "--shelves-per-product",
                                  type=check_positive, default=4,
                                  help="""the maximum number of shelves that contain the same
                                  product (default: %(default)s)""",
                                  dest="shelves_per_product")
        product_args.add_argument("--pus", "--product-units-per-product-shelf",
                                  type=check_positive, default=20,
                                  help="""the maximum number of each product's units per shelf
                                  (default: %(default)s)""",
                                  dest="product_units_per_product_shelf")

        order_args = parser.add_argument_group("Order constraints")
        order_args.add_argument("-o", "--orders", type=check_positive,
                                help="the number of orders")
        order_args.add_argument("--olmin", "--order-min-lines", type=check_positive,
                                default=1,
                                help="Specifies minimum of lines per order (default: %(default)s)",
                                dest="order_min_lines")
        order_args.add_argument("--olmax", "--order-max-lines", type=check_positive,
                                default=1,
                                help="Specifies maximum of lines per order (default: %(default)s)",
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
                                    components) in the floor grid (default: %(default)s)""")
        layout_hw_args = parser.add_argument_group("* Constraints for the *highway* layout")
        layout_hw_args.add_argument("-H", "--highway-layout", action="store_true",
                                    help="Manhattan-style street grid using highway-nodes")
        layout_hw_args.add_argument("-X", "--cluster-x", type=check_positive, default=2,
                                    help="""for highway-layout: the size of one rectangular shelf
                                    cluster in x-direction (default: %(default)s)""")
        layout_hw_args.add_argument("-Y", "--cluster-y", type=check_positive, default=2,
                                    help="""for highway-layout: the size of one rectangular shelf
                                    cluster in y-direction (default: %(default)s)""")
        layout_hw_args.add_argument("-B", "--beltway-width", type=check_positive, default=1,
                                    help="""for highway layout: the width of the beltway surrounding
                                    all shelf clusters (default: %(default)s)""")

        project_args = parser.add_argument_group("Projection and template options")
        project_args.add_argument("-T", "--template", nargs='*', type=str, default=[],
                                  help="""every created instance will contain all atoms
                                  defined in #program base of the template file(s) (default: %(default)s)""")
        project_args.add_argument("--prj-orders", action="store_true",
                                  help='project enumeration to order-related init/2 atoms')
        project_args.add_argument("--prj-warehouse", action="store_true",
                                  help='project enumeration to warehouse-related init/2 atoms')
        project_args.add_argument("--split", nargs=2, action='store', type=check_positive,
                                  metavar="NUM",
                                  help="""splits instances into warehouse and order-related facts;
                                  takes as arguments 1.) the number of warehouses and 2.) the orders
                                  per warehouse to create, resp.""")
        return parser, parser.parse_args(args, namespace)
