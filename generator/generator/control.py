#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""General Execution Control."""

import os
import sys
import math
import argparse
import logging
import copy
import glob
import signal
from collections import OrderedDict
import yaml
from pkg_resources import resource_filename

from generator.generator import BasicGenerator
from generator.generator_inc import IncrementalGenerator
from generator.generator_split import SplitGenerator
from generator.utils.auxiliary import check_positive, SmartFormatter, clone_args
from generator.utils.logger import setup_logger
from generator import release

LOG = logging.getLogger('custom')

class Control(object):
    """Runs BasicGenerator once or multiple times."""
    def __init__(self, args=None, parent=None):
        namespace = None
        if parent: # Carrying over settings from parent
            nsdict = {k: copy.deepcopy(v) for k, v in list(vars(parent.args).items())
                      if k != 'batch'}
            if parent.args.skip_existing_sub:
                nsdict['skip_existing'] = True
            namespace = argparse.Namespace(**nsdict)
        self._cl_parser, self._args = Control._parse_cl_args(args, namespace)
        self._args_dict = vars(self._args)
        self._args_dict['enc_dir'] = resource_filename('generator', 'encodings')
        self._args_dict['template_str'] = None
        if self._args.template == ['-']:
            self._args_dict['template'] = []
            self._args_dict['template_str'] = sys.stdin.read()
        if not parent:
            if self._args.grounding_stats and self._args.loglevel is logging.WARNING:
                setup_logger(logging.INFO)
                LOG.info("Implying verbose output due to \'--gstats\' flag")
            else:
                setup_logger(self._args.loglevel)
        self._check_related_cl_args()

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
        if self._args.grounding_stats:
            LOG.warn("Grounding stats activated! --> FOR ANALYTICAL PURPOSE ONLY, NOT SUITED FOR PRODUCTION!")
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
        elif self._args.gen_inc:
            self._gen_inc()
        else:
            self._gen_basic()

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
                    except Exception as exc:
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
        invocations, global_settings = self._getinvocs(content, parent_path)
        LOG.debug("Global settings: %s", str(global_settings))
        LOG.debug("Invocations:\n%s", '\n'.join(str(inv) for inv in invocations or [None]))
        # exit(1)
        return invocations, global_settings

    def _getinvocs(self, content, parent_path):
        global_settings = []
        invocations = []
        if isinstance(content, OrderedDict):
            for key, val in list(content.items()):
                if key == 'global_settings':
                    LOG.debug("Global settings found: %s", str(val))
                    global_settings.extend(self._conv_args_dict(val, parent_path))
                elif key == 'run_configs':
                    LOG.debug("Runs config found: %s", str(val))
                    invocations = self._walk_runs_config(val, parent_path)
                elif key in ['args', 'conf']:
                    raise ValueError("Wrong batch file format")
        else:
            raise ValueError("Wrong batch file format")
        return invocations, global_settings

    def _walk_runs_config(self, content, parent_path, invocations=None):
        LOG.debug("Input invocations:\n%s", '\n'.join(str(inv) for inv in invocations or [None]))
        invocations = invocations or [['-d', parent_path]]
        if isinstance(content, OrderedDict):
            output_invocs = []
            found_args_list = []
            nested = False
            if 'args' in content:
                val = content['args']
                LOG.debug("Args found: %s", str(val))
                if isinstance(val, list):
                    for args in val:
                        found_args_list.extend(
                            self._get_extended_invocations(invocations, parent_path, None, args))
                elif isinstance(val, OrderedDict):
                    found_args_list = self._get_extended_invocations(invocations, parent_path,
                                                                     None, val)
                else:
                    raise ValueError("For key 'args', the value must be a list or dict.")
            for key, val in [(key, val) for key, val in list(content.items()) if key != 'args']:
                LOG.debug("Config found: %s", key)
                nested = True
                subconf_invocs = None
                if key == 'conf':
                    subconf_invocs = self._walk_runs_config(val, parent_path, found_args_list)
                else:
                    if found_args_list:
                        subconf_invocs = self._get_extended_invocations(invocations[1:],
                                                                        parent_path, key, None)
                    else:
                        subconf_invocs = self._get_extended_invocations(invocations, parent_path,
                                                                        key, None)
                    for args in found_args_list:
                        _args = copy.deepcopy(args)
                        _args[1] = os.path.join(_args[1], key)
                        subconf_invocs.append(_args)
                    subconf_invocs = self._walk_runs_config(val, parent_path, subconf_invocs)
                output_invocs.extend(subconf_invocs)
            if not nested:
                output_invocs.extend(found_args_list)
        else:
            raise ValueError("Wrong batch file format")
        LOG.debug("Output invocations:\n%s", '\n'.join(str(inv) for inv in invocations or [None]))
        return output_invocs

    def _conv_args_dict(self, adict, parent_path):
        args = []
        rel_template_path = False
        for elm in [elm for tup in list(adict.items()) for elm in tup]:
            if isinstance(elm, list):
                args += [str(itm) for itm in elm]
            elif isinstance(elm, bool):
                if elm is False:
                    args.pop()
                else:
                    pass
            elif rel_template_path:
                args += [os.path.join(parent_path, elm)]
                rel_template_path = False
            elif (elm == '-T' or elm == '--template') and self._args.template_relative:
                rel_template_path = True
                args += [str(elm)]
            else:
                args += [str(elm)]
        return args

    def _get_extended_invocations(self, invocations, parent_path, rel_path=None, args=None):
        args = args or OrderedDict()
        rel_path = rel_path or ''
        _invocations = copy.deepcopy(invocations)
        for inv in _invocations:
            inv[1] = os.path.join(inv[1], rel_path)
            inv.extend(self._conv_args_dict(args, parent_path))
        return _invocations

    def _gen_basic(self):
        """Regular instance generation."""
        return BasicGenerator(self._args).generate()

    def _gen_inc(self):
        """Incremental generation of an instance."""
        return IncrementalGenerator(self._args, self._cl_parser).generate()

    def _gen_split(self):
        """Execution with split up warehouse and order instances."""
        return SplitGenerator(self._args, self._cl_parser).generate()

    def _check_related_cl_args(self):
        """Checks consistency of related command line args."""
        try:
            if self._args.shelves and self._args.shelf_coverage:
                raise ValueError("""Number of shelves specified by both quantity (-s) and
                coverage rate (--sc)""")
            if ((self._args.products and not self._args.product_units_total) or
                    (not self._args.products and self._args.product_units_total)):
                raise ValueError("""To specify products, at least the number of products and the
                product units total is required""")
            if (self._args.product_units_per_product_shelf and
                    (self._args.min_product_units_per_product_shelf !=
                     self._cl_parser.get_default('min_product_units_per_product_shelf') or
                     self._args.max_product_units_per_product_shelf !=
                     self._cl_parser.get_default('max_product_units_per_product_shelf'))):
                raise ValueError("""The exact value of product units per shelf (--pus) must not be
                stated together with a min (--pusmin) and/or max (--pusmax) value!""")
            if (self._args.products_per_shelf and
                    (self._args.min_products_per_shelf !=
                     self._cl_parser.get_default('min_products_per_shelf') or
                     self._args.max_products_per_shelf !=
                     self.cl_parser.get_default('max_products_per_shelf'))):
                raise ValueError("""The exact value of products per shelf (--prs) must not be stated
                together with a min (--prsmin) and/or max (--prsmax) value!""")
            if (self._args.shelves_per_product and
                    (self._args.min_shelves_per_product !=
                     self._cl_parser.get_default('min_shelves_per_product') or
                     self._args.max_shelves_per_product !=
                     self._cl_parser.get_default('max_shelves_per_product'))):
                raise ValueError("""The exact value of shelves per product (--spr) must not be
                stated together with a min (--sprmin) and/or max (--sprmax) value!""")
            if (self._args.order_lines and
                    (self._args.min_order_lines !=
                     self._cl_parser.get_default('min_order_lines') or
                     self._args.max_order_lines !=
                     self._cl_parser.get_default('max_order_lines'))):
                raise ValueError("""The exact value of lines per order (--ol) must not be stated
                together with a min (--olmin) and/or max (--olmax) value!""")
            if self._args.products and self._args.product_units_total:
                if self._args.products > self._args.product_units_total:
                    raise ValueError("""The product units total must be smaller or equal to number
                    of products""")
                elif (self._args.product_units_total >
                      self._args.products *
                      (self._args.product_units_per_product_shelf or
                       self._args.max_product_units_per_product_shelf) *
                      (self._args.shelves_per_product or
                       self._args.max_shelves_per_product)):
                    raise ValueError("""The product units total must equal or less than the
                    multiplication of
                    1.) the number of products (i.e., -P value)
                    2.) the maximum number of units per product and shelf (i.e., --pusmax value)
                    3.) the maximum number of shelves per product (i.e., --maxspr value).""")
            if self._args.min_order_lines > self._args.max_order_lines:
                raise ValueError("""Order lines minimum larger than maximum""")
            if self._args.threads > 1 and self._args.split:
                raise ValueError("""Only single threaded execution (-t 1) possible when splitting
                up (--split) instances""")
        except ValueError as verr:
            LOG.error("Conflicting command line arguments! %s", verr)
            exit(1)

    @staticmethod
    def _parse_cl_args(args=None, namespace=None):
        """Argument parsing method.

         Parses command line arguments by default or, alternatively, an optional list of arguments
         passed by parameter.

         :type args: A list of argument strings or None.
         :type namespace: An existing argparse.Namespace object to use instead of new one.

        """
        parser = argparse.ArgumentParser(prog='gen',
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
        basic_args.add_argument("-N", "--num", type=int, default=1,
                                help="the number of instances to create (default: %(default)s)")
        basic_args.add_argument("-C", "--console",
                                help="prints the instances to the console", action="store_true")
        # Toggle instance writing, enabled by default
        basic_args.add_argument("--write-instance", dest='write_instance',
                                help=argparse.SUPPRESS, action="store_false")
        # Selection which instance to write
        basic_args.add_argument("--write-selected", dest='write_selected', type=check_positive,
                                help=argparse.SUPPRESS)
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
        basic_args.add_argument("--instance-count", type=int,
                                help="""each instance gets the given integer as running number instead
                                of using its rank in the enumeration of clasp""")
        instance_count = basic_args.add_mutually_exclusive_group()
        instance_count.add_argument("--instance-count-offset", type=int,
                                    help="""each instance gets the given integer as offset added to its
                                    running number instead of using its rank in the enumeration of clasp""")
        instance_count.add_argument("-f", "--name-prefix", type=str, default="",
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
        basic_args.add_argument("--sopts, --solve-opts", nargs=1, type=str, dest='solve_opts',
                                help="""options pass-through of to underlying clingo process,
                                **intended for debugging only!**""")
        basic_args.add_argument("-I", "--gen-inc", action='store_true',
                                help="""use incremental instance generation; required for large
                                instances to reduce grounding size""")
        basic_args.add_argument("--im", "--inc-im", action='store_true', dest='inc_im',
                                help="""for inc-mode, activate output of intermediate instances
                                (default: %(default)s)""")
        basic_args.add_argument('-V', '--verbose', action='store_const', dest='loglevel',
                                const=logging.INFO, default=logging.WARNING,
                                help='verbose output (default: %(default)s)')
        basic_args.add_argument('-D', '--debug', action='store_const', dest='loglevel',
                                const=logging.DEBUG, default=logging.WARNING,
                                help='debug output (default: %(default)s)')
        # basic_args.add_argument('--gstats', action='store_true', dest='grounding_stats',
        #                         help="""WARNING: FOR DEBUGGING ONLY, DO NOT USE FOR PRODUCTION!
        #                         Shows grounding size statistics for each program part of the instance
        #                         generator encoding. (default: %(default)s)""")
        basic_args.add_argument('--gstats', nargs='?', const='stats', dest='grounding_stats', metavar="OPT",
                                help=("R|WARNING: FOR ANALYTICAL PURPOSE ONLY, DO NOT USE FOR PRODUCTION!\n"
                                      "Shows grounding size statistics for each program part of the instance\n"
                                      "generator encoding, takes optional argument %(metavar)s:\n"
                                      "  stats : shows the grounding size statistics (implied by default)\n"
                                      "  atoms : additionally shows the grounded program and output atoms & terms"))
        basic_args.add_argument('--aspif', nargs='?', const='print', dest='aspif', metavar="OPT",
                                help=("R|WARNING: FOR ANALYTICAL PURPOSE ONLY, DO NOT USE FOR PRODUCTION!\n"
                                      "Prints the current aspif program for each solving step of the instance\n"
                                      " generation, takes optional argument %(metavar)s:\n"
                                      "  print : print to stdout only (implied by default)\n"
                                      "  dump : additionally dumps the aspif programs in directory './_aspif'"))


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
        product_args.add_argument("-u", "--product-units-total", type=check_positive,
                                  help="the total number of product units stored in the warehouse")
        # #product-units per shelf
        product_args.add_argument("--pusmin", "--min-product-units-per-product-shelf",
                                  type=int, default=1, metavar='PUSMIN',
                                  help="""for each product an shelf it is stored on,
                                  the minimum number of stored units (default: %(default)s)""",
                                  dest="min_product_units_per_product_shelf")
        product_args.add_argument("--pusmax", "--max-product-units-per-product-shelf",
                                  type=int, default=10, metavar='PUSMAX',
                                  help="""for each product and shelf it stored on,
                                  the maximum number of stored units (default: %(default)s);
                                  deactivate with value < 1""",
                                  dest="max_product_units_per_product_shelf")
        product_args.add_argument("--pus", "--product-units-per-product-shelf",
                                  type=int, default=None, metavar='PUS',
                                  help="""for each product and shelf it is stored on,
                                  the exact number of stored units (default: %(default)s);
                                  shorthand for \'--pusmin %(metavar)s --pusmax %(metavar)s\'""",
                                  dest="product_units_per_product_shelf")
        # #products per shelf
        product_args.add_argument("--prsmin", "--min-products-per-shelf",
                                  type=int, default=0, metavar='MINPRS',
                                  help="""the minimum number of products per shelf
                                  (default: %(default)s)""",
                                  dest="min_products_per_shelf")
        product_args.add_argument("--prsmax", "--max-products-per-shelf",
                                  type=int, default=20, metavar='MAXPRS',
                                  help="""the maximum number of products per shelf
                                  (default: %(default)s); deactivate with value < 1""",
                                  dest="max_products_per_shelf")
        product_args.add_argument("--prs", "--products-per-shelf",
                                  type=int, default=None, metavar='PRS',
                                  help="""the number of products per shelf
                                  (default: %(default)s); shorthand for
                                   \'--prsmin %(metavar)s --prsmax %(metavar)s\'""",
                                  dest="products_per_shelf")
        # Conditional usage flag for --minprs required by incremental mode implementation
        product_args.add_argument("--conditional-min-products-per-shelf",
                                  dest='conditional_min_products_per_shelf',
                                  help=argparse.SUPPRESS, action="store_true")

        # #shelves per product
        product_args.add_argument("--sprmin", "--min-shelves-per-product",
                                  type=int, default=1, metavar='MINSPR',
                                  help="""the maximum number of shelves that contain the same
                                  product (default: %(default)s); deactivate with value < 1""",
                                  dest="min_shelves_per_product")
        product_args.add_argument("--sprmax", "--max-shelves-per-product",
                                  type=int, default=4, metavar='MAXSPR',
                                  help="""the maximum number of shelves that contain the same
                                  product (default: %(default)s); deactivate with value < 1""",
                                  dest="max_shelves_per_product")
        product_args.add_argument("--spr", "--shelves-per-product",
                                  type=int, default=None, metavar='SPR',
                                  help="""the maximum number of shelves that contain the same
                                  product (default: %(default)s); shorthand for
                                   \'--sprmin %(metavar)s --sprmax %(metavar)s\'""",
                                  dest="shelves_per_product")

        order_args = parser.add_argument_group("Order constraints")
        order_args.add_argument("-o", "--orders", type=check_positive,
                                help="the number of orders")
        order_args.add_argument("--olmin", "--min-order-lines", type=check_positive,
                                default=1, metavar='MINOL',
                                help="the minimum number of lines per order (default: %(default)s)",
                                dest="min_order_lines")
        order_args.add_argument("--olmax", "--max-order-lines", type=check_positive,
                                default=1, metavar='MAXOL',
                                help="the maximum number of lines per order (default: %(default)s)",
                                dest="max_order_lines")
        order_args.add_argument("--ol", "--order-lines", type=check_positive,
                                default=None, metavar='OL',
                                help="""the exact number lines per order (default: %(default)s);
                                shorthand for \'--olmin %(metavar)s --olmax %(metavar)s\'""",
                                dest="order_lines")
        #TODO: olpu
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
        layout_hw_args.add_argument("--ph-pickstas", type=check_positive, dest="ph_pickstas",
                                    default=1,
                                    help="""placeholder for picking stations, i.e., the number of
                                    picking stations expected to be added to the instance in the
                                    future; required for adequate clearance of grid nodes at the top
                                    if the amount of picking stations is not specified (default:
                                    %(default)s)""")
        layout_hw_args.add_argument("--ph-robots", type=check_positive, dest="ph_robots",
                                    default=1,
                                    help="""placeholder for robots, i.e., the number of robots
                                    expected to be added to the instance in the future; required for
                                    adequate clearance of grid nodes at the top if the amount of
                                    robots is not specified (default: %(default)s)""")

        project_args = parser.add_argument_group("Template and projection options")
        project_args.add_argument("-T", "--template", nargs='*', type=str, default=[],
                                  help="""every created instance will contain all atom defined
                                  in base program of the template file(s) (default: %(default)s);
                                  alternatively, with argument '-T -', template facts can be streamed in
                                  directly from stdin""")
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
