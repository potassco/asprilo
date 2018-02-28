---
layout: default
title: experiments
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is a collection of notes and data on our conducted experiments with [asprilo](index.md).

# Evaluation 2018-02

## General Setup

### System

- CPU: 2 x AMD Opteron(tm) Processor 6278 Server
- RAM: 256 GB
- 32 cores, 64 threads

### Solver

- [clingo 5.3.0 development snapshot](https://github.com/potassco/clingo/tree/wip)
- [clingcon 3.3.0](https://github.com/potassco/clingcon/tree/v3.3.0)
- [clingoDL 1.0.1](https://github.com/potassco/clingoDL)

### Test Runs

- Each test run is limited to 1 physical core/thread and 8 GB of RAM
- Minimal horizon (makespan) additionally provided as input for each run
- Timeout is 1800s, no extra timeout penalty at the moment
- For each instance, we run an additional test with an assignment that restricts robots to distinct shelves and pick stations for interactions

## Instances

-   All subsequent benchmarks are run with the instance set to be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/instances.tar.bz2).

    ```shell
    moo
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
    ```

-   Subsequently, we will use the naming convention `RxCxL` for structured instance layouts where
    - `R` is the number of rows of storage zones
    - `C` is the number of columns of storage zones
    - `L` is the length in x-coordinates of storage zones (hint: for structured layouts, the height
      in y-coordinates of storage zones is fixed to 2 by definition)
-   On the top level, the instances are divided up into three sizes of structured warehouse layouts:
    - 1x2x4 aka *small*
    - 2x3x5 aka *medium*
    - 4x5x8 aka *large*
-   Further, all instances have 100 percent of the storage zones covered by shelves.
-   For each instance holds:
    - the number of robots and orders is identical;
    - there are exactly as many products and product units as shelves;
    - each shelf holds exactly one product unit;
    - each order contains exactly one order line.
-   Instances are further categorized by incrementally increasing the number of robots:
    - For 1x2x4 layout size: increments of 2, 5, 8 and 11 robots and orders total)
    - For 2x3x5 layout size: increments of 5, 10, 15 and 19 robots and orders
    - For 4x5x8 layout size: increments of 12, 23, 35 and 46 robots and orders in total)
-   Created by invocations (increments as exclusive flags in curly brackets )
    -   1x2x4 (*small*):

        ```shell
        gen -x 11 -y 6 -X 4 -Y 2 -p 1 -s 16 -P 16 -u 16 -H {-r 2 -o 2 | -r 5 -o 5 | -r 8 -o 8 | -r 11 -o 11}
        ```

    -   2x3x5 (*medium*):

        ```shell
        gen -x 19 -y 9 -X 5 -Y 2 -p 3 -s 60 -P 60 -u 60 -H {-r 5 -o 5 | -r 10 -o 10 | -r 15 -o 15 | -r 19 -o 19}
        ```

    -   4x5x8 (*large*):

        ```shell
        gen -x 46 -y 15 -X 8 -Y 2 -p 10 -s 320 -P 320 -u 320 -H {-r 12 -o 12 | -r 23 -o 23 | -r 35 -o 35 | -r 46 -o 46}
        ```

-   30 instances per each increment and hence 120 per layout size and 360 instances in total


## M-Domain Results

### Setup

#### Tested Encodings

- [clingo: boolean encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/moo/encoding.lp)
- [clingcon: csp encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/moo/encoding.clp)
- [clingo: boolean encoding w/ split x,y-coordinates](https://github.com/potassco/asprilo-encodings/blob/restruct/moo/encoding-XY.lp)
- [clingoDL: difference-logic encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/moo/encoding.dlp)

#### Outcome

An in-depth analysis of the subsequent results can be found in our ICLP'18 paper.

1.  Runs without Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/m/res.ods).
    - The column heads `dispatch-1/boolean`, `=dispatch-1/boolean-XY`, `dispatch-1/csp`,
      `dispatch-1/dlp-s` and `dispatch-1/dlp-sp` denote the boolean, boolean w/ split x,y-coordinates,
      clingcon and difference logic encoding with 'strict' and 'strict -p' execution flag,
      respectively

2.  Runs with Assignment (only clingo boolean, clingcon csp tested!)

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/m/res-asg.ods)
    - The column heads `dispatch-1/boolean` and `dispatch-1/csp` denote the boolean, clingcon and difference logic encoding, respectively


## A-Domain Results

### Tested Encodings

- [clingo: boolean encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/mppd/encoding-q.lp)
- [clingcon: csp encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/mppd/encoding-q.clp)

### Outcome

1.  Runs without Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/a/res.ods).

2.  Runs with Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/a/res-asg.ods)


## B-Domain Results

### Tested Encodings

- [clingo: boolean encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/mppd/encoding-r.lp)
- [clingcon: csp encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/mppd/encoding-r.clp)

### Outcome

1.  Runs without Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/b/res.ods).

2.  Runs with Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/b/res-asg.ods)

## C-Domain Results

### Tested Encodings

- [clingo: boolean encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/mppd/encoding-0.lp)
- [clingcon: csp encoding](https://github.com/potassco/asprilo-encodings/blob/restruct/mppd/encoding-0.clp)

### Outcome

1.  Runs without Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/c/res.ods).

2.  Runs with Assignment

    - Result spreadsheet can be found [here](https://www.cs.uni-potsdam.de/~phil/asprilo/experiments/2018-02/c/res-asg.ods)
