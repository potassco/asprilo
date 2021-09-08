#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instance Generator Core."""

import os
import logging
import math
import copy
import glob
from generator.utils.auxiliary import clone_args
from generator.generator import BasicGenerator, InstanceGenerator

LOG = logging.getLogger('custom')

class SplitGenerator(InstanceGenerator):
    """Abstract instance generator class."""

    def __init__(self, conf_args, cl_parser):
        super(SplitGenerator, self).__init__(conf_args)
        self._cl_parser = cl_parser
        self._args_dict = vars(self._args)

    def _gen_basic(self):
        return BasicGenerator(self._args).generate()

    def _gen_inc(self):
        return BasicGenerator(self._args).generate()

    def generate(self):
        """Generation with split up warehouse and order instances."""
        if self._args.gen_inc:
            gen_func = self._gen_inc
        else:
            gen_func = self._gen_basic
        num_wh_inst, num_order_inst = self._args.split
        args_dict_bak = copy.deepcopy(vars(self._args))

        # warehouse instances
        self._cl_parser.parse_args(args=['-d', self._args.directory + '/warehouse_',
                                         '--instance-dir',
                                         '--prj-warehouse',
                                         '-N', str(num_wh_inst)],
                                   namespace=self._args)

        LOG.info("Creating **warehouses** using solve args: %s", str(self._args))
        dest_dirs = gen_func()[1]

        # orders instances and merge
        for winst in range(1, num_wh_inst+1):

            # orders only
            self._args_dict.clear()
            self._args_dict.update(copy.deepcopy(args_dict_bak))
            self._args_dict['oap'] = False
            path_to_warehouse_file = glob.glob(dest_dirs[winst-1] + '/*.lp')[0]
            self._cl_parser.parse_args(
                args=['-d', dest_dirs[winst-1],
                      '--instance-dir-suffix', '/orders',
                      '-T', path_to_warehouse_file,
                      '--prj-orders',
                      '-N', str(num_order_inst)],
                namespace=self._args)

            LOG.info("Creating **orders** using solve args: %s", str(self._args))
            gen_func()

            # merge
            for oinst in range(1, len(glob.glob(dest_dirs[winst-1] + '/orders/*.lp')) + 1):
                self._args_dict.clear()
                self._args_dict.update(copy.deepcopy(args_dict_bak))
                path_to_order_file = glob.glob(dest_dirs[winst-1] +
                                               '/orders/*N{0}.lp'.format(oinst))[0]
                self._cl_parser.parse_args(
                    args=['-d', dest_dirs[winst-1] + '/merged',
                          '-T', path_to_warehouse_file, path_to_order_file,
                          '--instance-count', str(oinst),
                          '-N', '1'],
                    namespace=self._args)
                LOG.info("Creating **merged instances** using solve args: %s", str(self._args))
                self._gen_basic()
