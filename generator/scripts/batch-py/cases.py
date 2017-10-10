#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test Cases.'''

from collections import OrderedDict

general_pars = '--olmin 4 --olmax 4'

def define_cases(dest_dir):

    cases = OrderedDict()

    # = Standard Cases =============================================================================

    # - 1x2x4 --------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/1x2x4'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  4 -p 1 -H'})
    __cases.append({'pars': '-r 1 -P  8 -u 24 -o 2'})
    __cases.append({'pars': '-r 2 -P 16 -u 48 -o 4'})
    __cases.append({'pars': '-r 4 -P 24 -u 72 -o 8'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s  8 -p 1 -H'})
    __cases.append({'pars': '-r 1 -P 16 -u  48 -o 2'})
    __cases.append({'pars': '-r 2 -P 32 -u  96 -o 4'})
    __cases.append({'pars': '-r 4 -P 48 -u 144 -o 8'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 12 -p 1 -H'})
    __cases.append({'pars': '-r 1 -P 24 -u  72 -o 2'})
    __cases.append({'pars': '-r 2 -P 38 -u 144 -o 4'})
    __cases.append({'pars': '-r 4 -P 72 -u 216 -o 8'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars' : '-x 11 -y 6 -X 4 -Y 2 -s 16 -p 1 -H'})
    __cases.append({'pars': '-r 1 -P 32 -u  96 -o 2'})
    __cases.append({'pars': '-r 2 -P 64 -u 192 -o 4'})
    __cases.append({'pars': '-r 4 -P 96 -u 288 -o 8'})


    # - 2x3x5 --------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/2x3x5'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 15 -p 3 -H'})
    __cases.append({'pars': '-r  3 -P  30 -u   90 -o 6'})
    __cases.append({'pars': '-r  6 -P  60 -u  180 -o 12'})
    __cases.append({'pars': '-r 12 -P  90 -u  270 -o 24'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars': '-x 19 -y  9 -X 5 -Y 2 -s 30 -p 3 -H'})
    __cases.append({'pars': '-r  3 -P  60 -u  180 -o  6'})
    __cases.append({'pars': '-r  6 -P 120 -u  270 -o 12'})
    __cases.append({'pars': '-r 12 -P 180 -u  540 -o 24'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars': ' -x 19 -y  9 -X 5 -Y 2 -s 45 -p 3 -H'})
    __cases.append({'pars': '-r  3 -P  90 -u  270 -o  6'})
    __cases.append({'pars': '-r  6 -P 180 -u  540 -o 12'})
    __cases.append({'pars': '-r 12 -P 270 -u  810 -o 24'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars': '-x  19 -y  9 -X 5 -Y 2 -s 60 -p 3 -H'})
    __cases.append({'pars': '-r  3 -P 120 -u  540 -o  6'})
    __cases.append({'pars': '-r  6 -P 240 -u  810 -o 12'})
    __cases.append({'pars': '-r 12 -P 360 -u 1080 -o 24'})


    # - 4x5x8 --------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/4x5x8'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 80 -p  10 -H'})
    __cases.append({'pars': '-r 10 -P  160 -u  480 -o  20'})
    __cases.append({'pars': '-r 20 -P  320 -u  960 -o  40'})
    __cases.append({'pars': '-r 40 -P  480 -u 1440 -o  80'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 160 -p  10 -H'})
    __cases.append({'pars': '-r 10 -P  320 -u  960 -o  20'})
    __cases.append({'pars': '-r 20 -P  640 -u 1440 -o  40'})
    __cases.append({'pars': '-r 40 -P  960 -u 2880 -o  80'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 240 -p  10 -H'})
    __cases.append({'pars': '-r 10 -P  480 -u 1440 -o  20'})
    __cases.append({'pars': '-r 20 -P  960 -u 2880 -o  40'})
    __cases.append({'pars': '-r 40 -P 1440 -u 4320 -o  80'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars': '-x  46 -y  15 -X   8 -Y  2 -s 320 -p  10 -H'})
    __cases.append({'pars': '-r 10 -P  640 -u 1920 -o  20'})
    __cases.append({'pars': '-r 20 -P 1280 -u 3840 -o  40'})
    __cases.append({'pars': '-r 40 -P 1920 -u 5760 -o  80'})


    # - 7x8x10 -------------------------------------------------------------------------------------
    _cases = cases['standard_cases/rectangles/7x8x10'] = OrderedDict()

    # -- 25sc --------------------------------------------------------------------------------------
    __cases = _cases['25sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  280 -p  23 -H'})
    __cases.append({'pars': '-r 10 -P  560 -u  1680 -o  10'})
    __cases.append({'pars': '-r 20 -P 1220 -u  3360 -o  40'})
    __cases.append({'pars': '-r 40 -P 1680 -u  5040 -o 160'})

    # -- 50sc --------------------------------------------------------------------------------------
    __cases = _cases['50sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  560 -p  23 -H'})
    __cases.append({'pars': '-r 10 -P 1120 -u  3360 -o  10'})
    __cases.append({'pars': '-r 20 -P 2240 -u  6720 -o  40'})
    __cases.append({'pars': '-r 40 -P 3360 -u 10080 -o 160'})

    # -- 75sc --------------------------------------------------------------------------------------
    __cases = _cases['75sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s  840 -p  23 -H'})
    __cases.append({'pars': '-r 10 -P 1680 -u  5040 -o  10'})
    __cases.append({'pars': '-r 20 -P 3360 -u 10080 -o  40'})
    __cases.append({'pars': '-r 40 -P 5040 -u 15120 -o 160'})

    # -- 100sc -------------------------------------------------------------------------------------
    __cases = _cases['100sc'] = []
    __cases.append({'template': True, 'pars': '-x 89 -y  24 -X  10 -Y  2 -s 1120 -p  23 -H'})
    __cases.append({'pars': '-r 10 -P 2240 -u  6720 -o  10'})
    __cases.append({'pars': '-r 20 -P 4480 -u 13440 -o  40'})
    __cases.append({'pars': '-r 40 -P 6720 -u 20160 -o 160'})

    return cases
