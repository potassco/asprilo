#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instance Generator Core."""


import logging
import math
from generator.utils.auxiliary import clone_args
from generator.generator import BasicGenerator, InstanceGenerator

LOG = logging.getLogger('custom')

class IncrementalGeneratorLegacy(InstanceGenerator):
    """Abstract instance generator class."""

    def __init__(self, conf_args, cl_parser):
        super(IncrementalGeneratorLegacy, self).__init__(conf_args)
        self._cl_parser = cl_parser

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
        if not self._args.inc_im and self._args.picking_stations:
            args_dict['write_instance'] = False
        else:
            args_dict['write_instance'] = True
        LOG.info("\n** INC MODE: Generating Grid *******************************************")
        LOG.debug("Creating grid based on args: %s", str(args))
        templates, dest_dirs = self._gen_basic(args)
        args_dict['template_str'] = templates[0]

        # Add picking stations to instance
        args_dict['picking_stations'] = self._args.picking_stations
        if not self._args.inc_im and self._args.robots:
            args_dict['write_instance'] = False
        else:
            args_dict['write_instance'] = True
        LOG.info("\n** INC MODE: Generating Picking Stations ********************************")
        LOG.debug("Creating picking stations based on args: %s", str(args))
        templates, dest_dirs = self._gen_basic(args)
        args_dict['template_str'] = templates[0]
        args_dict['picking_stations'] = None

        # Add robots to instance
        args_dict['robots'] = self._args.robots
        if not self._args.inc_im and self._args.shelves:
            args_dict['write_instance'] = False
        else:
            args_dict['write_instance'] = True
        LOG.info("\n** INC MODE: Generating Robots ******************************************")
        LOG.debug("Creating robots based on args: %s", str(args))
        args_dict['template_str'] = self._gen_basic(args)[0][0]
        args_dict['robots'] = None
        args_dict['num'] = self._args.num

        # Incrementally add shelves
        if self._args.shelves:
            LOG.info("\n** INC MODE: Generating Shelves ****************************************")
            grid_template = args_dict['template_str']
            templates = []
            dest_dirs = []
            for select in range(self._args.num):
                LOG.info("\n** INC MODE: Adding shelves to previous template %s", str(select + 1))
                args_dict['template_str'] = grid_template
                template, _dest_dirs = self._add_objs_inc({'shelves' : [self._args.shelves, 20]},
                                                          args, not self._args.products, select,
                                                          select + 1)
                templates.append(template)
                dest_dirs.extend(_dest_dirs)

        # Incrementally add product units
        if self._args.products:
            LOG.info("\n** INC MODE: Generating Products and Product Units *********************")
            prev_templates = templates
            templates = []
            dest_dirs = []
            ratio_untits_vs_products = int(math.floor(self._args.product_units_total /
                                                      self._args.products))
            if 5 <= ratio_untits_vs_products < 100:
                inc_products = int(math.floor(100 / ratio_untits_vs_products))
                inc_product_units = 100
            elif ratio_untits_vs_products < 5:
                inc_products = 40
                inc_product_units = 40 * ratio_untits_vs_products
            else:
                inc_products = 1
                inc_product_units = ratio_untits_vs_products
            for select in range(self._args.num):
                LOG.info("\n** INC MODE: Adding products and product units to previous template %s",
                         str(select))
                args_dict['template_str'] = prev_templates[select]
                template, _dest_dirs = self._add_objs_inc(
                    {'products' : [self._args.products, inc_products],
                     'product_units_total' : [self._args.product_units_total, inc_product_units]},
                    args, not self._args.orders, select, select + 1)
                templates.append(template)
                dest_dirs.extend(_dest_dirs)

        # Incrementally add orders
        if self._args.orders:
            LOG.info("\n **INC MODE: Generating Orders *****************************************")
            prev_templates = templates
            templates = []
            dest_dirs = []
            for select in range(self._args.num):
                LOG.info("\n** INC MODE: Adding orders to previous template %s", str(select))
                args_dict['template_str'] = prev_templates[select]
                template, _dest_dirs = self._add_objs_inc(
                    {'orders': [self._args.orders,
                                int(math.floor(10 / self._args.order_min_lines or 1))]},
                    args, True, select, select + 1)
                templates.append(template)
                dest_dirs.extend(_dest_dirs)
        return templates, list(set(dest_dirs))

    def _add_objs_inc(self, objs_settings, args, output=False, select=0, instance_count=None):
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
            if (output and len(maxed_objs) == len(objs_settings)) or self._args.inc_im:
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
