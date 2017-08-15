---
layout: page
title: visualizer
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the user manual of the instance and plan visualizer of [ASPRILO](index.md).


# Invocation

The script `./visualizer/scripts/visualizer` provides an visualizer with various option, for
a detailed list invoke

    ./visualizer/scripts/visualizer -h


# Requirements


## Overview

The visualizer requires the following software installed on your system:

1. [clingo5](http://github.com/potassco/clingo), version 5.3.0 or later
2. [Python interpreter version 2.7.x](http://www.python.org)
3. [Qt5](http://qt-project.org/qt5)
4. [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/installation.html), version 5.6 or later


## Building PyQt5 from Source Code

We assume that python an Qt5 are already installed on your system.

### SIP Installation

1.  Download

        wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.1/sip-4.19.1.tar.gz
        tar -xzvf sip-4.19.1.tar.gz

2.  Configuration

    -   In case you install sip system-wide, enter:

            cd sip-4.19.1
            python configure.py

    -   In case you are using a virtual environment, enter:

            cd sip-4.19.1
            python configure.py --deployment-target=10.12 \
                                --destdir=${VIRTUAL_ENV}/lib/python2.7/site-packages \
                                --incdir=${VIRTUAL_ENV}/include/python2.7

        Make sure that the environment variable `VIRTUAL_ENV` is set to the path of your virtual python environment.

3.  Building and Installation

        make
        make install


### PyQt5 Installation

1.  Download

        wget https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.8.1/PyQt5_gpl-5.8.1.tar.gz
        tar -xzvf PyQt5_gpl-5.8.1.tar.gz

2.  Configuration

    -   In case you install sip system-wide, enter:

            cd PyQt5_gpl-5.8.1
            python configure.py --verbose

    -   In case you are using a virtual environment, enter:

            cd PyQt5_gpl-5.8.1
            python configure.py --sip=${VIRTUAL_ENV}/bin/sip \
                                    --sip-incdir=${VIRTUAL_ENV}/include/python2.7/ \
                                    --verbose

    For both cases, make sure that `qmake` is in your path. Alternatively, add
    `--qmake=<path-to-qmake-bin>` as additional argument to the invocation of the `configure.py`
    script above.

3.  Building and Installation

        make
        make install


# Usage

TODO
