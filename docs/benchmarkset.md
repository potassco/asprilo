---
layout: page
title: Benchmark Set
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the description of the pre-generated benchmark instance sets for asprilo.

# Instance Sets

The latest [asprilo release](https://github.com/potassco/asprilo/releases) provides a set of
pre-generated instances `instances.tar.gz` with the following directory structure:

    ├── abc
    │   └── structured
    │       ├── 1x2x4
    │       │   ├── 100sc
    │       │   ├── 25sc
    │       │   ├── 50sc
    │       │   └── 75sc
    │       ├── 2x3x5
    │       │   ├── 100sc
    │       │   ├── 25sc
    │       │   ├── 50sc
    │       │   └── 75sc
    │       └── 4x5x8
    │           ├── 100sc
    │           ├── 25sc
    │           ├── 50sc
    │           └── 75sc
    └── moo
        └── structured
            ├── 1x2x4
            │   └── 100sc
            │       ├── r02
            │       ├── r05
            │       ├── r08
            │       └── r11
            ├── 2x3x5
            │   └── 100sc
            │       ├── r05
            │       ├── r10
            │       ├── r15
            │       └── r19
            └── 4x5x8
                └── 100sc
                    ├── r12
                    ├── r23
                    ├── r35
                    └── r46

The instances are partitioned into two parts:

-   `./abc`:
    - A structured instance set suited for domain A,B and C
    - Created by the [instance generator](generator.md) with batch file
      [`./generator/scripts/batch/abc/structured.yml`]({{ site.asprilo_src_url }}/generator/scripts/batch/abc/structured.yml)

-   `./moo`:
    - A structured instance set primarily designed for domain M but by definition also compatible
      with domain A, B, C
    - Created by the [instance generator](generator.md) with batch file
      [`./generator/scripts/batch/moo/structured.yml`]({{ site.asprilo_src_url }}/generator/scripts/batch/moo/structured.yml)


Further, we group instances into directories with naming convention `RxCxL` where

- `R` is the number of rows of storage zones
- `C` is the number of columns of storage zones
- `L` is the length in x-coordinates of storage zones (hint: for structured layouts, the height in
   y-coordinates of storage zones is fixed to 2 by definition)

for each contained instance. That is, instances are divided up in both `./abc/structured` and `./moo/structured` into three sizes
of structured warehouse layouts:

    - `./1x2x4` for instance with 1 row and 2 columns of storage zones where the x-dimension of storage zones is 4
    - `./2x3x5` for instance with 2 row and 3 columns of storage zones where the x-dimension of storage zones is 5
    - `./4x5x8` for instance with 4 row and 5 columns of storage zones where the x-dimension of storage zones is 8

In addition to that, we further distinguish instances based on the percentage of storage nodes covered by shelves. E.g. within
`/abc/structured/1x2x4` the four directories `25sc`, `50sc`, `75sc` and `100sc` hold instances with 25%, 50%, 75% and 100% storage coverage by shelves, respectively.

For `/.moo` instances, we further differentiate between the number of robots as detailed ![here](experiments.md).
