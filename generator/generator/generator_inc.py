#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instance Generator Core."""


import os
import logging
import math
from clingo.control import Control
from generator.utils.auxiliary import clone_args
from generator.generator import BasicGenerator, InstanceGenerator

LOG = logging.getLogger('custom')

class IncrementalGenerator(InstanceGenerator):
    """Abstract instance generator class."""

    def __init__(self, conf_args, cl_parser):
        super(IncrementalGenerator, self).__init__(conf_args)
        self._cl_parser = cl_parser
        self._selected_facts = []

    def _gen_basic(self, conf_args):
        return BasicGenerator(conf_args).generate()

    def generate(self):
        """Incremental generation of an instance."""
        LOG.info(("** INCREMENTAL MODE ****************************************************\n"
                  "Incremental instance generation for initial args: %s"), str(self._args))

        # Generate instance that contains only the grid
        args = clone_args(self._cl_parser, self._args)
        args_dict = vars(args)
        args_dict['picking_stations'] = None
        args_dict['robots'] = None
        args_dict['shelves'] = None
        args_dict['products'] = None
        args_dict['product_units_total'] = None
        args_dict['orders'] = None
        args_dict['num'] = 1
        if not self._args.inc_im:
            args_dict['write_instance'] = False
        else:
            args_dict['write_instance'] = True
        LOG.info("\n** INC MODE: Generating Grid *******************************************")
        LOG.debug("Creating grid based on args: %s", str(args))
        templates, dest_dirs = self._gen_basic(args)
        args_dict['grid_x'] = None
        args_dict['grid_y'] = None

        # Add picking stations to instance
        if self._args.picking_stations:
            input_instance = templates[0]
            args_dict['template_str'] = FactFilter(self._args, input_instance, 'picking_stations', []).apply()
            args_dict['picking_stations'] = self._args.picking_stations
            if not self._args.inc_im:
                args_dict['write_instance'] = False
            else:
                args_dict['write_instance'] = True
            LOG.info("\n** INC MODE: Generating Picking Stations ********************************")
            LOG.debug("Creating picking stations based on args: %s", str(args))
            templates, dest_dirs = self._gen_basic(args)
            templates[0] += input_instance
            args_dict['picking_stations'] = None
        # Add robots to instance
        if self._args.robots:
            input_instance = templates[0]
            args_dict['template_str'] = FactFilter(self._args, input_instance, 'robots', []).apply()
            args_dict['robots'] = self._args.robots
            if not self._args.inc_im:
                args_dict['write_instance'] = False
            else:
                args_dict['write_instance'] = True
            LOG.info("\n** INC MODE: Generating Robots ******************************************")
            LOG.debug("Creating robots based on args: %s", str(args))
            templates, dest_dirs = self._gen_basic(args)
            templates[0] += input_instance
            args_dict['robots'] = None

       # self._dump_instances([args_dict['template_str']]) #TODO generalize for all stages and num > 1
        args_dict['num'] = self._args.num
        args_dict['highway_layout'] = False

        # Incrementally add shelves
        if self._args.shelves:
            LOG.info("\n** INC MODE: Generating Shelves ****************************************")
            input_instance = templates[0]
            grid_template = FactFilter(self._args, input_instance, 'shelves', []).apply()
            # grid_template = args_dict['template_str']
            templates = []
            dest_dirs = []
            for select in range(self._args.num):
                LOG.info("\n** INC MODE: Adding shelves to previous template %s", str(select + 1))
                args_dict['template_str'] = grid_template
                template, _dest_dirs = self._add_objs_inc({'shelves' : [self._args.shelves, 20]},
                                                          args, select, select + 1)
                templates.append(template + input_instance)
                dest_dirs.extend(_dest_dirs)

        # Incrementally add product units
        if self._args.products:
            LOG.info("\n** INC MODE: Generating Products and Product Units *********************")
            prev_templates = templates
            filtered_templates = [FactFilter(self._args, instance, 'products', []).apply()
                                  for instance in prev_templates]
            templates = []
            dest_dirs = []
            ratio_untits_vs_products = int(math.floor(self._args.product_units_total /
                                                      self._args.products))
            args_dict['conditional_min_products_per_shelf'] = True
            if 5 <= ratio_untits_vs_products < 100:
                inc_products = int(math.floor(100 / ratio_untits_vs_products))
                inc_product_units = 100
            elif ratio_untits_vs_products < 5:
                inc_products = 40
                inc_product_units = 40 * ratio_untits_vs_products
            else:
                inc_products = 1
                inc_product_units = ratio_untits_vs_products
            args_dict['order_all_products'] = False
            for select in range(self._args.num):
                LOG.info("\n** INC MODE: Adding products and product units to previous template %s",
                         str(select + 1))
                args_dict['template_str'] = filtered_templates[select]
                template, _dest_dirs = self._add_objs_inc(
                    {'products' : [self._args.products, inc_products],
                     'product_units_total' : [self._args.product_units_total, inc_product_units]},
                    args, select, select + 1)
                templates.append(template + prev_templates[select])
                dest_dirs.extend(_dest_dirs)
            args_dict['order_all_products'] = self._args.order_all_products

        # Incrementally add orders
        if self._args.orders:
            LOG.info("\n **INC MODE: Generating Orders *****************************************")
            prev_templates = templates
            filtered_templates = [FactFilter(self._args, instance, 'orders', []).apply()
                                  for instance in prev_templates]
            templates = []
            dest_dirs = []
            for select in range(self._args.num):
                LOG.info("\n** INC MODE: Adding orders to previous template %s", str(select + 1))
                args_dict['template_str'] = filtered_templates[select]
                template, _dest_dirs = self._add_objs_inc(
                    {'orders': [self._args.orders,
                                int(math.floor(10 / self._args.min_order_lines or 1))]},
                    args, select, select + 1)
                templates.append(template + prev_templates[select])
                dest_dirs.extend(_dest_dirs)
        LOG.info("\n **INC MODE: Writing complete instances to output ***************************")
        self._dump_instances(templates)
        return templates, list(set(dest_dirs))

    def _add_objs_inc(self, objs_settings, args, select=0, instance_count=None):
        """Incremental adds objects of a given type to an instance and returns result."""
        args_dict = vars(args)
        maxed_objs = []
        args_dict['instance_count'] = instance_count
        while len(maxed_objs) < len(objs_settings):
            for setting in list(objs_settings.items()):
                otype, (max_count, inc_size) = setting
                args_dict[otype] = args_dict[otype] or 0
                if args_dict[otype] + inc_size < max_count:
                    args_dict[otype] += inc_size
                else:
                    args_dict[otype] = max_count
                    maxed_objs.append(otype)
            if maxed_objs and len(maxed_objs) < len(objs_settings):
                continue
            if (len(maxed_objs) == len(objs_settings) and self._args.inc_im):
                args_dict['write_instance'] = True
                args_dict['write_selected'] = select + 1
            templates, dest_dirs = self._gen_basic(args)
            if len(templates) > select:
                args_dict['template_str'] = templates[select]
            else:
                args_dict['template_str'] = templates[-1]
        for otype in objs_settings:
            args_dict[otype] = None
        args_dict['write_instance'] = False
        args_dict['write_selected'] = None
        args_dict['instance_count'] = None
        return args_dict['template_str'], dest_dirs

    def _dump_instances(self, instances):
        """Writes instance to file."""
        args = clone_args(self._cl_parser, self._args)
        args_dict = vars(args)
        args_dict['picking_stations'] = None
        args_dict['robots'] = None
        args_dict['shelves'] = None
        args_dict['products'] = None
        args_dict['product_units_total'] = None
        args_dict['orders'] = None
        args_dict['grid_x'] = None
        args_dict['grid_y'] = None
        args_dict['num'] = 1
        args_dict['highway_layout'] = None
        args_dict['write_instance'] = True
        for idx, instance in enumerate(instances):
            args_dict['template_str'] = instance
            args_dict['instance_count'] = idx + 1
            LOG.info("\n **INC MODE: Writing instance %s", idx+1)
            BasicGenerator(args).generate()



class FactFilter(object):
    """Selects relevant facts for incremental generator stages."""

    def __init__(self, conf_args, instance, stage, stage_args):
        """Init.

        :param conf_args: argspace.Namespace holding all configuration settings
        :param str instance: Input ASP instance
        :param str stage: ASP program name for filtering facts of next incremental generation stage
        :param list stage_args: List of ASP program integer parameters required for grounding

        """
        self._args = conf_args
        self._instance = instance
        self._stage = stage
        self._stage_args = stage_args
        self._selected_facts = ''

    def apply(self):
        "Returns filtered facts."
        prg = Control()
        prg.add('base', [], self._instance)
        prg.load(os.path.join(self._args.enc_dir, 'inc_filter.lp'))
        prg.ground([('base', [])])
        prg.ground([(self._stage, self._stage_args)])
        prg.ground([('project', [])])
        self._selected_facts = ''
        prg.solve(on_model=self._stash_selected_facts)
        LOG.debug("Relevant facts for adding %s: %s", self._stage, self._selected_facts)
        return self._selected_facts

    def _stash_selected_facts(self, model):
        self._selected_facts = '.\n'.join([str(atm) for atm in model.symbols(terms=True)]) + "."
