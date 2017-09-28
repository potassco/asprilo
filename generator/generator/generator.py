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

    def on_model(self, model):
        """Call back method for clingo."""
        self._instance_count += 1
        self._inits = []
        if self._args.console:
            print "\n"
            LOG.info("~~~~ %s. Instance ~~~~", str(self._instance_count))
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
        for template in self._args.template:
            self._prg.load(template)
            self._prg.ground([("base", [])])
            self._prg.ground([("template_stub", [])])

        LOG.info("Grounding...")

        # nodes
        if not (self._args.grid_x is None or self._args.grid_y is None):
            if self._args.nodes is None:
                self._prg.ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                             self._args.grid_x * self._args.grid_y])])
            else:
                self._prg.ground([("nodes", [self._args.grid_x, self._args.grid_y,
                                             self._args.nodes])])
        # object quantities and IDs
        if self._args.robots:
            self._prg.ground([("robots", [self._args.robots, self._args.robots])])
        if self._args.shelves:
            self._prg.ground([("shelves", [self._args.shelves, self._args.shelves])])
        if self._args.picking_stations:
            self._prg.ground([("picking_stations",
                               [self._args.picking_stations, self._args.picking_stations])])
        if self._args.products:
            self._prg.ground([("products", [self._args.products, self._args.products])])
        if self._args.orders:
            self._prg.ground([("orders", [self._args.orders])])

        # layouts
        if self._args.highway_layout:
            self._prg.ground([("highway_layout", [self._cluster_x, self._cluster_y,
                                                  self._args.beltway_width])])
        else:
            self._prg.ground([("random_layout", [self._args.gap_size])])

        # object quantities and IDs contd.: depending on layout definitions
        if self._args.shelf_coverage:
            self._prg.ground([("shelf_coverage", [self._args.shelf_coverage])])

        # object inits
        self._prg.ground([("robots_init", [])])
        self._prg.ground([("shelves_init", [])])
        self._prg.ground([("picking_stations_init", [])])
        if self._args.product_units_total:
            self._prg.ground([("product_units", [self._args.product_units_total,
                                                 self._args.product_units_total,
                                                 self._args.product_units_per_product_shelf])])
        self._prg.ground([("orders_init", [self._args.order_min_lines,
                                           self._args.order_max_lines])])

        # layouts contd.: constraints related to interior object placement
        # TODO: simplify grounding order of layouts, constraints, object inits program parts
        # - use init/2 instead of poss/2 in layout constraints above
        if self._args.reachable_shelves:
            self._prg.ground([("reachable_shelves", [])])


        # order constraints & optimizations
        if self._args.order_all_products:
            self._prg.ground([("order_all_products", [])])
        # self._prg.ground([("orders_different", [])])

        # general rules
        self._prg.ground([("base", [])])

        # projection to subsets of init/2
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

        LOG.info("Parallel mode: %s", str(self._prg.configuration.solve.parallel_mode))
        LOG.info("Generated instances: %s", str(self._instance_count))
        LOG.info("Solve result: %s", str(solve_result))
        LOG.info("Search finished: %s", str(not solve_result.interrupted))
        LOG.info("Search space exhausted: %s", str(solve_result.exhausted))

    def _save(self):
        """Writes instance to file."""
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
        try:
            with open(file_name, "w") as ofile:
                #head
                ofile.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                ofile.write("\n% Grid Size X:                      " + str(self._object_counters["x"]))
                ofile.write("\n% Grid Size Y:                      " + str(self._object_counters["y"]))
                ofile.write("\n% Number of Nodes:                  " + str(self._object_counters["node"]))
                ofile.write("\n% Number of Highway Nodes:          " + str(self._object_counters["highway"]))
                ofile.write("\n% Number of Robots:                 " + str(self._object_counters["robot"]))
                ofile.write("\n% Number of Shelves:                " + str(self._object_counters["shelf"]))
                ofile.write("\n% Number of Picking Stations:       " + str(self._object_counters["pickingStation"]))
                ofile.write("\n% Number of Products:               " + str(self._object_counters["product"]))
                ofile.write("\n% Number of Product Units in Total: " + str(self._object_counters["units"]))
                ofile.write("\n% Number of Orders:                 " + str(self._object_counters["order"]))
                ofile.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

                #body
                ofile.write("#program base.\n\n")
                # if not (self._args.grid_x is None or self._args.grid_y is None):
                #     ofile.write("timelimit("+ str(int(self._args.grid_x * self._args.grid_y * 1.5))
                #                 + ").\n\n")
                ofile.write("% init\n")
                for obj in self._inits:
                    ofile.write(str(obj) + ".\n")
        except IOError as err:
            LOG.error("IOError while trying to write instance file \'%s\': %s", file_name, err)
        return

    def interrupt(self):
        '''Kill all solve call threads.'''
        self._prg.interrupt()
