#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instance Generator Core."""

import os
import logging
import clingo

LOG = logging.getLogger('custom')

class InstanceGenerator(object):

    def __init__(self, args):

        self._args = args
        self._prg = None
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

    def on_model(self, model):
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
        LOG.info("Stats: %s", {k: int(v) for k, v in self._object_counters.items()})
        self._save()

    def _update_object_counter(self, atoms_list):
        '''Count objects in atom list.'''
        self._object_counters = {"x" : 0, "y" : 0, "node" : 0, "highway" :0, "robot" : 0, "shelf" :
                                 0, "pickingStation" : 0, "product" : 0, "order" : 0, "units" : 0}
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
        """Grounds and solves the relevant programs for instance generation."""
        LOG.debug("Used args for grounding & solving: %s", str(self._args))

        self._prg = clingo.Control(self._solve_opts)
        self._prg.load(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    '../encodings/ig.lp'))

        # Templates
        for template in self._args.template:
            self._prg.load(template)
        if self._args.template_str:
            self._prg.add("base", [], self._args.template_str)
        self._prg.ground([("base", [])])
        if self._args.template or self._args.template_str:
            self._prg.ground([("template_stub", [])])

        LOG.info("Grounding...")

        # Nodes
        if self._args.grid_x and self._args.grid_y:
            if self._args.nodes is None:
                self._prg.ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                             self._args.grid_x * self._args.grid_y])])
            else:
                self._prg.ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                             self._args.nodes])])

        # Floor dimensions and total number nodes (grounded independently to also support floor
        # templates)
        self._prg.ground([("floor_dimensions", [])])

        # Object quantities and IDs
        if self._args.robots:
            self._prg.ground([("robots_cl", [self._args.robots, self._args.robots])])
        self._prg.ground([("robots", [])])

        if self._args.shelves:
            self._prg.ground([("shelves_cl", [self._args.shelves, self._args.shelves])])
        self._prg.ground([("shelves", [])])

        if self._args.picking_stations:
            self._prg.ground([("picking_stations_cl",
                               [self._args.picking_stations, self._args.picking_stations])])
        self._prg.ground([("picking_stations", [])])

        if self._args.products:
            self._prg.ground([("products_cl", [self._args.products, self._args.products])])
        self._prg.ground([("products", [])])

        if self._args.orders:
            self._prg.ground([("orders", [self._args.orders])])

        # Layouts
        if self._args.highway_layout:
            self._prg.ground([("highway_layout", [self._cluster_x, self._cluster_y,
                                                  self._args.beltway_width,
                                                  self._args.ph_pickstas, self._args.ph_robots])])
        else:
            self._prg.ground([("random_layout", [])])
            if self._args.grid_x and self._args.grid_y and self._args.nodes:
                self._prg.ground([("grid_gaps", [self._args.gap_size])])

        # Object quantities and IDs contd.: depending on layout definitions
        if self._args.shelf_coverage:
            self._prg.ground([("shelf_coverage", [self._args.shelf_coverage])])

        # Object inits
        self._prg.ground([("robots_init", [])])
        self._prg.ground([("shelves_init", [])])
        self._prg.ground([("picking_stations_init", [])])
        if self._args.product_units_total:
            self._prg.ground([("product_units", [self._args.product_units_total,
                                                 self._args.product_units_total,
                                                 self._args.products_per_shelf,
                                                 self._args.shelves_per_product,
                                                 self._args.product_units_per_product_shelf or
                                                 self._args.product_units_total])])
        self._prg.ground([("orders_init", [self._args.order_min_lines,
                                           self._args.order_max_lines])])

        # Layouts contd.: constraints related to interior object placement
        # TODO: simplify grounding order of layouts, constraints, object inits program parts
        # - use init/2 instead of poss/2 in layout constraints above
        if self._args.reachable_shelves:
            self._prg.ground([("reachable_shelves", [])])


        # Order constraints & optimizations
        if self._args.order_all_products:
            self._prg.ground([("order_all_products", [])])
        # self._prg.ground([("orders_different", [])])

        # General rules
        self._prg.ground([("base", [])])
        self._prg.ground([("symmetry", [])])

        # Projection to subsets of init/2
        if self._args.prj_orders:
            self._prg.ground([("project_orders", [])])
        elif self._args.prj_warehouse:
            self._prg.ground([("project_warehouse", [])])
        else:
            self._prg.ground([("project_all", [])])

        LOG.info("Solving...")

        # solve_future = self._prg.solve_async(self.on_model)
        # solve_future.wait(self._args.wait)
        # solve_future.cancel()
        # solve_result = solve_future.get()

        solve_result = self._prg.solve(on_model=self.on_model)

        if self._args.write_selected and self._args.write_selected > len(self._instances):
            LOG.warn("Selected instance %s not written since not enumerated, i.e., "
                     "only enumerated %s!",
                     str(self._args.write_selected), str(len(self._instances)))

        LOG.info("Parallel mode: %s", str(self._prg.configuration.solve.parallel_mode))
        LOG.info("Generated instances: %s", str(self._instance_count))
        LOG.info("Solve result: %s", str(solve_result))
        LOG.info("Search finished: %s", str(not solve_result.interrupted))
        LOG.info("Search space exhausted: %s", str(solve_result.exhausted))
        LOG.debug("Statistics: %s", self._prg.statistics)

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

        # Instance preamble
        instance = ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
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
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
        instance = instance.format(str(self._object_counters["x"]),
                                   str(self._object_counters["y"]),
                                   str(self._object_counters["node"]),
                                   str(self._object_counters["highway"]),
                                   str(self._object_counters["robot"]),
                                   str(self._object_counters["shelf"]),
                                   str(self._object_counters["pickingStation"]),
                                   str(self._object_counters["product"]),
                                   str(self._object_counters["units"]),
                                   str(self._object_counters["order"]))

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
