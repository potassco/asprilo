#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Custom Logger."""

import sys
import logging

class SingleLevelFilter(logging.Filter):
    def __init__(self, passlevel, reject):
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record):
        if self.reject:
            return (record.levelno != self.passlevel)
        else:
            return (record.levelno == self.passlevel)

def setup_logger(level=logging.INFO):
    """Logger setup."""

    logger = logging.getLogger('custom')
    logger.propagate = False
    logger.setLevel(level)

    # INFO stream handler
    info_sh = logging.StreamHandler(sys.stdout)
    info_sh.addFilter(SingleLevelFilter(logging.INFO, False))
    info_sh.setLevel(logging.INFO)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(levelname)s: %(relativeCreated)s - %(message)s')
    info_sh.setFormatter(formatter)
    logger.addHandler(info_sh)

    # WARNING stream handleer
    warn_sh = logging.StreamHandler(sys.stdout)
    warn_sh.addFilter(SingleLevelFilter(logging.WARNING, False))
    warn_sh.setLevel(logging.WARN)
    formatter = logging.Formatter('%(levelname)s: %(relativeCreated)s %(filename)s:%(funcName)s:%(lineno)d  - %(message)s')
    warn_sh.setFormatter(formatter)
    logger.addHandler(warn_sh)

    # DEBUG stream handler
    debug_sh = logging.StreamHandler(sys.stdout)
    debug_sh.addFilter(SingleLevelFilter(logging.DEBUG, False))
    debug_sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s: %(relativeCreated)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s')
    debug_sh.setFormatter(formatter)
    logger.addHandler(debug_sh)

    # ERROR stream handler
    error_sh = logging.StreamHandler(sys.stdout)
    error_sh.addFilter(SingleLevelFilter(logging.ERROR, False))
    error_sh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s: %(relativeCreated)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s')
    error_sh.setFormatter(formatter)
    logger.addHandler(error_sh)
