---
layout: page
title: generator
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the user manual of the instance generator of [ASPRILO](index.md).


# Invocation

The script `./generator/ig.py` provides an instance generator with various option, for
a detailed list invoke

    python ./generator/ig.py -h


## Example Invocations: Warehouse Only

-   Real-world-like, Symmetrical Instances

    -   WH with 40% shelf coverage of storage nodes

            ig.py -x 20 -y 20 -r 4 -X 3 -Y 2 -p 3  -H -R -B 2 --sc 40

    -   Large WH

            ig.py -x 57 -y 50 -r 20 -X 10 -Y 2 -p 10 -H -R -B 2

    -   Now with shelves, long comp time

            ig.py -x 57 -y 50 -r 20 -X 10 -Y 2 -p 10 -s 300 -H -R -B 2

-   Random Instances

    -   Large

            ig.py -x 50 -y 50 -r 20 -X 10 -Y 2 -s 100 -p 10

    -   Small

            ig.py -x 10 -y 10 -r 20 -X 10 -Y 2 -s 30 -p 5
