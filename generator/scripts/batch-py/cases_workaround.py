#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test Cases.'''

from collections import OrderedDict

general_pars = '--olmin 3 --olmax 3'


def define_cases(dest_dir):
    cases = OrderedDict()

    # = Standard Cases =============================================================================

    # - 1x2x4 --------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/1x2x4'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  4 -p 1 -r 1 -H', 'suffix': 'r1_pre'})
    __cases.append({'template': True, 'pars': '-P  8 -u 24', 'suffix': 'r1'})
    __cases.append({'pars': '-o 2'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  4 -p 1 -r 2 -H', 'suffix': 'r2_pre'})
    __cases.append({'template': True, 'pars': '-P 16 -u 48', 'suffix': 'r2'})
    __cases.append({'pars': '-o 4'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  4 -p 1 -r 4 -H', 'suffix': 'r4_pre'})
    __cases.append({'template': True, 'pars': '-P 24 -u 72', 'suffix': 'r4'})
    __cases.append({'pars': '-o 8'})
    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  8 -p 1 -r 1 -H', 'suffix': 'r1_pre'})
    __cases.append({'template': True, 'pars': '-P 16 -u  48', 'suffix': 'r1'})
    __cases.append({'pars': '-o 2'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  8 -p 1 -r 2 -H', 'suffix': 'r2_pre'})
    __cases.append({'template': True, 'pars': '-P 32 -u  96', 'suffix': 'r2'})
    __cases.append({'pars': '-o 4'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  8 -p 1 -r 4 -H', 'suffix': 'r4_pre'})
    __cases.append({'template': True, 'pars': '-P 48 -u 144', 'suffix': 'r4'})
    __cases.append({'pars': '-o 8'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 12 -p 1 -r 1 -H', 'suffix': 'r1_pre'})
    __cases.append({'template': True, 'pars': '-P 24 -u  72', 'suffix': 'r1'})
    __cases.append({'pars': '-o 2'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 12 -p 1 -r 2 -H', 'suffix': 'r2_pre'})
    __cases.append({'template': True, 'pars': '-P 38 -u 144', 'suffix': 'r2'})
    __cases.append({'pars': '-o 4'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 12 -p 1 -r 4 -H', 'suffix': 'r4_pre'})
    __cases.append({'template': True, 'pars': '-P 72 -u 216', 'suffix': 'r4'})
    __cases.append({'pars': '-o 8'})

    # # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 16 -p 1 -r 1 -H', 'suffix': 'r1_pre'})
    __cases.append({'template': True, 'pars': '-P 32 -u  96', 'suffix': 'r1'})
    __cases.append({'pars': '-o 2'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 16 -p 1 -r 2 -H', 'suffix': 'r2_pre'})
    __cases.append({'template': True, 'pars': '-P 64 -u 192', 'suffix': 'r2'})
    __cases.append({'pars': '-o 4'})
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 16 -p 1 -r 4 -H', 'suffix': 'r4_pre'})
    __cases.append({'template': True, 'pars': '-P 96 -u 288', 'suffix': 'r4'})
    __cases.append({'pars': '-o 8'})


    # - 2x3x5 --------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/2x3x5'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 15 -p 3 -r  3 -H', 'suffix': 'r3_pre'})
    __cases.append({'template': True, 'pars': '-P  30 -u  90', 'suffix': 'r3'})
    __cases.append({'pars': '-o 6'})
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 15 -p 3 -r  6 -H', 'suffix': 'r6_pre'})
    __cases.append({'template': True, 'pars': '-P  60 -u 180', 'suffix': 'r6'})
    __cases.append({'pars': '-o 12'})
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 15 -p 3 -r 12 -H', 'suffix': 'r12_pre'})
    __cases.append({'template': True, 'pars': '-P  90 -u  270', 'suffix': 'r12'})
    __cases.append({'pars': '-o 24'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 30 -p 3 -r  3 -H', 'suffix': 'r3_pre'})
    __cases.append({'template': True, 'pars': '-P  60 -u  180', 'suffix': 'r3'})
    __cases.append({'pars': '-o  6'})
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 30 -p 3 -r  6 -H', 'suffix': 'r6_pre'})
    __cases.append({'template': True, 'pars': ' -P 120 -u  270', 'suffix': 'r6'})
    __cases.append({'pars': ' -o 12'})
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 30 -p 3 -r 12 -H', 'suffix': 'r12_pre'})
    __cases.append({'template': True, 'pars': '-P 180 -u  540', 'suffix': 'r12'})
    __cases.append({'pars': '-o 24'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 45 -p 3 -r  3 -H', 'suffix': 'r3_pre'})
    __cases.append({'template': True, 'pars': '-P  90 -u  270', 'suffix': 'r3'})
    __cases.append({'pars': ' -o  6'})
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 45 -p 3 -r  6 -H', 'suffix': 'r6_pre'})
    __cases.append({'template': True, 'pars': '-P 180 -u  540', 'suffix': 'r6'})
    __cases.append({'pars': '-o 12'})
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 45 -p 3 -r 12 -H', 'suffix': 'r12_pre'})
    __cases.append({'template': True, 'pars': '-P 270 -u  810', 'suffix': 'r12'})
    __cases.append({'pars': '-o 24'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars': '-x  19 -y  9 -X 5 -Y 2 -s 60 -p 3 -r  3 -H', 'suffix': 'r3_pre'})
    __cases.append({'template': True, 'pars': '-P 120 -u  540', 'suffix': 'r3'})
    __cases.append({'pars': '-o  6'})
    __cases.append({'template': True, 'pars': '-x  19 -y  9 -X 5 -Y 2 -s 60 -p 3 -r  6 -H', 'suffix': 'r6_pre'})
    __cases.append({'template': True, 'pars': '-P 240 -u  810', 'suffix': 'r6'})
    __cases.append({'pars': '-o 12'})
    __cases.append({'template': True, 'pars': '-x  19 -y  9 -X 5 -Y 2 -s 60 -p 3 -r 12 -H', 'suffix': 'r12_pre'})
    __cases.append({'template': True, 'pars': '-P 360 -u 1080', 'suffix': 'r12'})
    __cases.append({'pars': '-o 24'})


    # - 4x5x8 --------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/4x5x8'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 80 -p  10 -r 10 -H', 'suffix': 'r10_pre'})
    __cases.append({'template': True, 'pars': '-P  160 -u  480 ', 'suffix': 'r10'})
    __cases.append({'pars': '-o  20'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 80 -p  10 -r 20 -H', 'suffix': 'r20_pre'})
    __cases.append({'template': True, 'pars': '-P  320 -u  960 ', 'suffix': 'r20'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 80 -p  10 -r 40 -H', 'suffix': 'r40_pre'})
    __cases.append({'template': True, 'pars': '-P  480 -u 1440 ', 'suffix': 'r40'})
    __cases.append({'pars': '-o  80'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 160 -p  10 -r 10 -H', 'suffix': 'r10_pre'})
    __cases.append({'template': True, 'pars': '-P  320 -u  960 ', 'suffix': 'r10'})
    __cases.append({'pars': '-o  20'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 160 -p  10 -r 20 -H', 'suffix': 'r20_pre'})
    __cases.append({'template': True, 'pars': '-P  640 -u 1440 ', 'suffix': 'r20'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 160 -p  10 -r 40 -H', 'suffix': 'r40_pre'})
    __cases.append({'template': True, 'pars': '-P  960 -u 2880 ', 'suffix': 'r40'})
    __cases.append({'pars': '-o  80'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 240 -p  10 -r 10 -H', 'suffix': 'r10_pre'})
    __cases.append({'template': True, 'pars': '-P  480 -u 1440 ', 'suffix': 'r10'})
    __cases.append({'pars': '-o  20'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 240 -p  10 -r 20 -H', 'suffix': 'r20_pre'})
    __cases.append({'template': True, 'pars': '-P  960 -u 2880 ', 'suffix': 'r20'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 240 -p  10 -r 40 -H', 'suffix': 'r40_pre'})
    __cases.append({'template': True, 'pars': '-P 1440 -u 4320 ', 'suffix': 'r40'})
    __cases.append({'pars': '-o  80'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 320 -p  10 -r 10 -H', 'suffix': 'r1_pre0'})
    __cases.append({'template': True, 'pars': '-P  640 -u 1920 ', 'suffix': 'r10'})
    __cases.append({'pars': '-o  20'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 320 -p  10 -r 20 -H', 'suffix': 'r2_pre0'})
    __cases.append({'template': True, 'pars': '-P 1280 -u 3840 ', 'suffix': 'r20'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 320 -p  10 -r 40 -H', 'suffix': 'r4_pre0'})
    __cases.append({'template': True, 'pars': '-P 1920 -u 5760 ', 'suffix': 'r40'})
    __cases.append({'pars': '-o  80'})


    # - 7x8x10 -------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/7x8x10'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  280 -p  23 -r 23 -H', 'suffix': 'r23_pre'})
    __cases.append({'template': True, 'pars': '-P  560 -u  1680', 'suffix': 'r23'})
    __cases.append({'pars': '-o  10'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  280 -p  23 -r 46 -H', 'suffix': 'r46_pre'})
    __cases.append({'template': True, 'pars': '-P 1220 -u  3360', 'suffix': 'r46'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  280 -p  23 -r 69 -H', 'suffix': 'r69_pre'})
    __cases.append({'template': True, 'pars': '-P 1680 -u  5040', 'suffix': 'r69'})
    __cases.append({'pars': '-o 160'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  560 -p  23 -r 23 -H', 'suffix': 'r23_pre'})
    __cases.append({'template': True, 'pars': '-P 1120 -u  3360', 'suffix': 'r23'})
    __cases.append({'pars': '-o  10'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  560 -p  23 -r 46 -H', 'suffix': 'r46_pre'})
    __cases.append({'template': True, 'pars': '-P 2240 -u  6720', 'suffix': 'r46'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  560 -p  23 -r 69 -H', 'suffix': 'r69_pre'})
    __cases.append({'template': True, 'pars': '-P 3360 -u 10080', 'suffix': 'r69'})
    __cases.append({'pars': '-o 160'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  840 -p  23 -r 23 -H', 'suffix': 'r23_pre'})
    __cases.append({'template': True, 'pars': '-P 1680 -u  5040', 'suffix': 'r23'})
    __cases.append({'pars': '-o  10'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  840 -p  23 -r 46 -H', 'suffix': 'r46_pre'})
    __cases.append({'template': True, 'pars': '-P 3360 -u 10080', 'suffix': 'r46'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  840 -p  23 -r 69 -H', 'suffix': 'r69_pre'})
    __cases.append({'template': True, 'pars': '-P 5040 -u 15120', 'suffix': 'r69'})
    __cases.append({'pars': '-o 160'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s 1120 -p  23 -r 23 -H', 'suffix': 'r23_pre'})
    __cases.append({'template': True, 'pars': '-P 2240 -u  6720', 'suffix': 'r23'})
    __cases.append({'pars': '-o  10'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s 1120 -p  23 -r 46 -H', 'suffix': 'r46_pre'})
    __cases.append({'template': True, 'pars': '-P 4480 -u 13440', 'suffix': 'r46'})
    __cases.append({'pars': '-o  40'})
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s 1120 -p  23 -r 69 -H', 'suffix': 'r69_pre'})
    __cases.append({'template': True, 'pars': '-P 6720 -u 20160', 'suffix': 'r69'})
    __cases.append({'pars': '-o 160'})

    return cases
