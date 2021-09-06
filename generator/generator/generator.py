#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instance Generator Core."""

import os
import sys
import signal
import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime
from clingo.control import Control
from clingo.symbol import Number
from .observer import Observer
from .aspif import AspifObserver

LOG = logging.getLogger('custom')

class InstanceGenerator(object):
    """Abstract instance generator class."""

    def __init__(self, conf_args, *args):
        """Init.

        :param conf_args: argspace.Namespace holding all configuration settings

        """
        self._args = conf_args

    @abstractmethod
    def generate(self):
        """Generates and returns the instances based on its configuration settings."""
        pass

class BasicGenerator(InstanceGenerator):
    """Most basic instance generator implementation."""

    def __init__(self, conf_args):
        super(BasicGenerator, self).__init__(conf_args)
        self._prg = None
        self._observer = Observer()
        self._aspif_obs = AspifObserver()
        self._solve_opts = ["-t {0}".format(self._args.threads),
                            "--project",
                            # "--opt-mode=optN",
                            "-n {0}".format(self._args.num)]
        if self._args.random:
            self._solve_opts.extend(['--rand-freq={}'.format(self._args.rand_freq),
                                     '--sign-def={}'.format(self._args.sign_def),
                                     '--seed={}'.format(self._args.seed)])
        if self._args.solve_opts:
            self._solve_opts.extend(self._args.solve_opts)
        self._inits = None
        self._object_counters = {}
        self._instance_count = 0
        self._instances = []
        self.dest_dirs = []

        if self._args.cluster_x is None:
            self._cluster_x = int((self._args.grid_x - 2 + 0.5) / 2)
        else:
            self._cluster_x = self._args.cluster_x
        if self._args.cluster_y is None:
            self._cluster_y = int((self._args.grid_y - 4 + 0.5) / 2)
        else:
            self._cluster_y = self._args.cluster_y

    def _on_model(self, model):
        """Call back method for clingo."""
        self._instance_count += 1
        self._inits = []
        if self._args.console:
            LOG.info("\n~~~~ %s. Instance ~~~~", str(self._instance_count))
        atoms_list = model.symbols(terms=True)
        LOG.debug("Found model: %s", '.\n'.join([str(atm) for atm in model.symbols(atoms=True)]))
        atm = None
        for atm in [atm for atm in atoms_list if atm.name == "init"]:
            self._inits.append(atm)
        self._update_object_counter(atoms_list)
        LOG.info("Stats: %s", {k: int(v) for k, v in list(self._object_counters.items())})
        self._save()

    def _update_object_counter(self, atoms_list):
        '''Count objects in atom list.'''
        self._object_counters = {"x" : 0, "y" : 0, "node" : 0, "highway" :0, "robot" : 0, "shelf" :
                                 0, "pickingStation" : 0, "product" : 0, "unit" : 0, "order" : 0, "line" : 0}
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
                        self._object_counters["unit"] = (self._object_counters["unit"] +
                                                         value_value.arguments[1].number)
                if object_name == "order" and args[1].arguments[0].name == 'line':
                    self._object_counters["line"] += 1

    def generate(self):
        """Regular instance generation.

        :param args: Optional argparse.Namespace.

        """
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
        try:
            signal.alarm(self._args.wait)
            instances = self._solve()
            return instances, self.dest_dirs
        except Exception as exc:
            if sig_handled[0]:
                pass
            else:
                logging.exception(exc)
        finally:
            self.interrupt()

    def _solve(self):
        """Grounds and solves the relevant programs for instance generation."""
        LOG.debug("Used args for grounding & solving: %s", str(self._args))

        self._prg = Control(self._solve_opts)

        # Register ground program observer to analyze grounding size impact per program parts
        self._prg.register_observer(self._observer)

        # Register ground program observer for aspif output of current ground program
        self._prg.register_observer(self._aspif_obs)

        # Problem encoding
        self._prg.load(os.path.join(self._args.enc_dir, 'ig.lp'))

        # Templates
        for template in self._args.template:
            self._prg.load(template)
        if self._args.template_str:
            self._prg.add("base", [], self._args.template_str)
        self._ground([("base", [])])
        if self._args.template or self._args.template_str:
            self._ground([("template_stub", [])])

        LOG.info("Grounding...")

        # Nodes
        if self._args.grid_x and self._args.grid_y:
            if self._args.nodes is None:
                self._ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                         self._args.grid_x * self._args.grid_y])])
            else:
                self._ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                         self._args.nodes])])

        # Floor dimensions and total number nodes (grounded independently to also support floor
        # templates)
        self._ground([("floor_dimensions", [])])

        # Object quantities and IDs
        if self._args.robots:
            self._ground([("robots_cl", [self._args.robots, self._args.robots])])
        self._ground([("robots", [])])

        if self._args.shelves:
            self._ground([("shelves_cl", [self._args.shelves, self._args.shelves])])
        self._ground([("shelves", [])])

        if self._args.picking_stations:
            self._ground([("picking_stations_cl",
                           [self._args.picking_stations, self._args.picking_stations])])
        self._ground([("picking_stations", [])])

        if self._args.products:
            self._ground([("products_cl", [self._args.products, self._args.products])])
        self._ground([("products", [])])

        if self._args.orders:
            self._ground([("orders", [self._args.orders])])

        # Layouts
        if self._args.highway_layout:
            self._ground([("highway_layout", [self._cluster_x, self._cluster_y,
                                              self._args.beltway_width,
                                              self._args.ph_pickstas, self._args.ph_robots])])
        else:
            self._ground([("random_layout", [])])
            if self._args.grid_x and self._args.grid_y and self._args.nodes:
                self._ground([("grid_gaps", [self._args.gap_size])])

        # Object quantities and IDs contd.: depending on layout definitions
        if self._args.shelf_coverage:
            self._ground([("shelf_coverage", [self._args.shelf_coverage])])

        # Object inits
        self._ground([("robots_init", [])])
        self._ground([("shelves_init", [])])
        self._ground([("picking_stations_init", [])])
        if self._args.product_units_total:
            self._ground([("product_units", [
                # min
                self._args.product_units_total,
                # max
                self._args.product_units_total,
                # minpus
                self._args.product_units_per_product_shelf or
                self._args.min_product_units_per_product_shelf or 1,
                # maxpus
                self._args.product_units_per_product_shelf or
                self._args.max_product_units_per_product_shelf or
                self._args.product_units_total,
                # minprs
                self._args.products_per_shelf or
                self._args.min_products_per_shelf or 0,
                # maxprs
                self._args.products_per_shelf or
                self._args.max_products_per_shelf or
                self._args.products,
                # minspr
                self._args.shelves_per_product or
                self._args.min_shelves_per_product or 0,
                # maxspr
                self._args.shelves_per_product or
                self._args.max_shelves_per_product or
                self._args.shelves,
                # cnd_minpsr
                1 if self._args.conditional_min_products_per_shelf else 0])])
        self._ground([("orders_init", [
            # minlines
            self._args.order_lines or
            self._args.min_order_lines or 1,
            # maxlines
            self._args.order_lines or
            self._args.max_order_lines,
            # maxpupr
            ((self._args.product_units_per_product_shelf or
              self._args.max_product_units_per_product_shelf) *
             (self._args.shelves_per_product or
              self._args.max_shelves_per_product)) or
            self._args.product_units_total])])

        # Layouts contd.: constraints related to interior object placement
        # TODO: simplify grounding order of layouts, constraints, object inits program parts
        # - use init/2 instead of poss/2 in layout constraints above
        if self._args.reachable_shelves:
            self._ground([("reachable_shelves", [])])

        # Order constraints & optimizations
        if self._args.order_all_products:
            self._ground([("order_all_products", [])])
        # self._ground([("orders_different", [])])

        # General rules
        self._ground([("base", [])])
        self._ground([("symmetry", [])])

        # Projection to subsets of init/2
        if self._args.prj_orders:
            self._ground([("project_orders", [])])
        elif self._args.prj_warehouse:
            self._ground([("project_warehouse", [])])
        else:
            self._ground([("project_all", [])])

        if self._args.aspif:
            self._print_aspif("AFTER GROUNDING, BEFORE CONCLUDING SOLVE CALL", self._args.aspif)

        LOG.info("Solving...")

        # solve_future = self._prg.solve_async(self._on_model)
        # solve_future.wait(self._args.wait)
        # solve_future.cancel()
        # solve_result = solve_future.get()

        solve_result = self._prg.solve(on_model=self._on_model)

        if self._args.write_selected and self._args.write_selected > len(self._instances):
            LOG.warn("Selected instance %s not written since not enumerated, i.e., "
                     "only enumerated %s!",
                     str(self._args.write_selected), str(len(self._instances)))

        LOG.info("Parallel mode: %s", str(self._prg.configuration.solve.parallel_mode))
        LOG.info("Generated instances: %s", str(self._instance_count))
        LOG.info("Solve result: %s", str(solve_result))
        LOG.info("Search finished: %s", str(not solve_result.interrupted))
        LOG.info("Search space exhausted: %s", str(solve_result.exhausted))
        import json
        LOG.debug("Statistics: %s", json.dumps(self._prg.statistics, sort_keys=True, indent=4,
                                               separators=(',', ': ')))

        if self._args.grounding_stats:
            self._print_grounding_stats("AFTER CONCLUDING SOLVE CALL", self._args.grounding_stats)

        return self._instances

    def _save(self):
        """Writes instance to file."""
        file_name = ''
        if (not self._args.write_instance or
                (self._args.write_selected and self._args.write_selected != self._instance_count)):
            file_name = os.devnull
        elif self._args.console:
            file_name = "/dev/stdout"
        else:
            if self._args.instance_count:
                instance_count = self._args.instance_count
            elif self._args.instance_count_offset:
                instance_count = self._instance_count + self._args.instance_count_offset
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
                                    "u" + str(self._object_counters["unit"]),
                                    "o" + str(self._object_counters["order"]),
                                    "l" + str(self._object_counters["line"]),
                                    "N" + str(instance_count).zfill(3)]))
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

        # Instance preamble
        instance = ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                    "%\n"
                    "% = Command-line Arguments =================================\n"
                    "% {}\n"
                    "%\n"
                    "% = Instance Statistics ====================================\n"
                    "% Grid Size X:                      {}\n"
                    "% Grid Size Y:                      {}\n"
                    "% Number of Nodes:                  {}\n"
                    "% Number of Highway Nodes:          {}\n"
                    "% Number of Robots:                 {}\n"
                    "% Number of Shelves:                {}\n"
                    "% Number of Picking Stations:       {}\n"
                    "% Number of Products:               {}\n"
                    "% Number of Product Units in Total: {}\n"
                    "% Number of Orders:                 {}\n"
                    "% Number of Orders Lines:           {}\n"
                    "%\n"
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
        instance = instance.format(" ".join(sys.argv[1:]),
                                   str(self._object_counters["x"]),
                                   str(self._object_counters["y"]),
                                   str(self._object_counters["node"]),
                                   str(self._object_counters["highway"]),
                                   str(self._object_counters["robot"]),
                                   str(self._object_counters["shelf"]),
                                   str(self._object_counters["pickingStation"]),
                                   str(self._object_counters["product"]),
                                   str(self._object_counters["unit"]),
                                   str(self._object_counters["order"]),
                                   str(self._object_counters["line"]))

        # Instance facts
        instance += ("#program base.\n\n"
                     "% init\n")
        self._inits.sort()
        for init in self._inits:
            instance += str(init) + ".\n"
        self._instances.append(instance)
        try:
            with open(file_name, "w") as ofile:
                ofile.write(instance)
        except IOError as err:
            LOG.error("IOError while trying to write instance file \'%s\': %s", file_name, err)

    def interrupt(self):
        '''Kill all solve call threads.'''
        self._prg.interrupt()

    def _ground(self, parts, context=None):
        """For grounding self._prg, wrapper of Control.ground to include optional statistics.

        """
        self._prg.ground([(name, [Number(par) for par in pars] or []) for (name, pars) in parts],
                         context)
        if self._args.grounding_stats:
            description = 'parts: ' + str(parts)
            if context:
                description += '| context: ' + str(context)
            self._print_grounding_stats(description, self._args.grounding_stats)

    def _print_grounding_stats(self, description=None, show='stats'):
        """Prints the grounding size statistics for current ASP program."""
        self._prg.ground([("project_all", [])])
        self._prg.solve()
        ctx = self._observer.finalize()
        prg = Control()
        prg.load(os.path.join(self._args.enc_dir, 'grnd_stats.lp'))
        if show == 'stats':
            prg.add('base', [], '#show stats/2. #show stats_total/1.')
        elif show == 'atoms':
            pass
        else:
            raise ValueError("Unsupported grounding stats option \'{}\'".format(show))
        prg.add("observed", [], "o(@get()).")
        prg.ground([('base', []), ("observed", [])], ctx)
        def __on_model(model):
            LOG.info(("Grounding size stats for program %s:\n"
                      "                                                %s\n"),
                     description,
                     ", ".join([str(sym) for sym in model.symbols(shown=True)]))
        prg.solve(on_model=__on_model)

    def _print_aspif(self, description=None, output='print', dump_dir='./_aspif'):
        """Prints the aspif program of the current Control object stored in self._prg."""
        self._prg.solve()
        ctx = self._aspif_obs.finalize()
        aspif = 'asp 1 0 0\n'
        for stype, statements in list(ctx.get().items()):
            for stm in statements:
                aspif += str(stype) + ' ' + ' '.join([str(sym) for sym in stm]) + '\n'
        aspif += '0'
        if output == 'print':
            LOG.info(("ASPIF output of current program %s:\n"
                      "%s\n"),
                     description,
                     aspif)
        elif output == 'dump':
            try:
                os.makedirs(dump_dir)
            except OSError:
                if not os.path.isdir(dump_dir):
                    raise
            now = datetime.now().strftime("%H:%M:%S.%f")
            with open('{}/dump_{}'.format(dump_dir, now), 'w') as wfile:
                wfile.write(aspif)
        else:
            raise ValueError("Unsupported aspif output option \'{}\'".format(output))
