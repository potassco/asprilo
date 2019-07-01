---
layout: page
title: Generator
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the user manual of the instance generator of [asprilo](index.md).

# Installation

We **highly recommend** to install the generator with [conda](https://conda.io/):

1.  [Install either Anaconda or Miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
2.  [Create and activate a fresh conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), e.g. via

    ``` bash
    conda create -n myenv
    conda activate myenv
    ```

3.  To install the generator in your environment, run

    ``` bash
    conda install -c potassco asprilo-generator
    ```

4.  Run

    ``` bash
    gen -h
    ```

    to verify that the generator installed correctly.

## Manual Installation (Not Supported!)

Alternatively, you can install the generator manually by downloading its source code from
[https://github.com/potassco/asprilo](https://github.com/potassco/asprilo). However, you must install all
requirements by yourself and probably adjust some environment variables (e.g. `PATH`, `PYTHONPATH`).
Please note that this method is **not supported**!

## Requirements

For manual installation, the generator requires the following software installed on
your system:

1. [clingo5](http://github.com/potassco/clingo)>=5.3.0
2. [Python interpreter version >=3.6.x](http://www.python.org)
3. [PyYAML](https://github.com/yaml/pyyaml)>=3.12

# Usage

The script `./generator/scripts/gen` provides an instance generator with various configuration options, for
a detailed list and description run

    gen -h
    usage: gen [-h] [-x GRID_X] [-y GRID_Y] [-n NODES] [-r ROBOTS] [-s SHELVES]
           [--sc SHELF_COVERAGE] [-p PICKING_STATIONS] [-N NUM] [-C]
           [-d DIRECTORY] [--se] [--instance-dir]
           [--instance-dir-suffix INSTANCE_DIR_SUFFIX]
           [--instance-count INSTANCE_COUNT] [-f NAME_PREFIX] [-v]
           [-t THREADS] [-w WAIT] [--random] [--rand-freq PERCENTAGE]
           [--sign-def DEFAULT_SIGN] [--seed SEED]
           [--sopts, --solve-opts SOLVE_OPTS] [-I] [--im] [-V] [-D]
           [--gstats [OPT]] [-j JOB] [-c [CAT [CAT ...]]] [--su] [--tr]
           [--preo] [--pret] [-P PRODUCTS] [-u PRODUCT_UNITS_TOTAL]
           [--pusmin PUSMIN] [--pusmax PUSMAX] [--pus PUS] [--prsmin MINPRS]
           [--prsmax MAXPRS] [--prs PRS] [--sprmin MINSPR] [--sprmax MAXSPR]
           [--spr SPR] [-o ORDERS] [--olmin MINOL] [--olmax MAXOL] [--ol OL]
           [--oap] [-R] [--gs GAP_SIZE] [-H] [-X CLUSTER_X] [-Y CLUSTER_Y]
           [-B BELTWAY_WIDTH] [--ph-pickstas PH_PICKSTAS]
           [--ph-robots PH_ROBOTS] [-T [TEMPLATE [TEMPLATE ...]]]
           [--prj-orders] [--prj-warehouse] [--split NUM NUM]

    Basic options:
      -h, --help            Show this help message and exit
      -x GRID_X, --grid-x GRID_X
                            the grid size in x-direction
      -y GRID_Y, --grid-y GRID_Y
                            the grid size in y-direction
      -n NODES, --nodes NODES
                            the number of nodes
      -r ROBOTS, --robots ROBOTS
                            the number of robots
      -s SHELVES, --shelves SHELVES
                            the number of shelves
      --sc SHELF_COVERAGE, --shelf-coverage SHELF_COVERAGE
                            the percentage of storage nodes covered by shelves;
                            storage nodes are those nodes that are not a highway
                            node nor occupied by a robot or station
      -p PICKING_STATIONS, --picking-stations PICKING_STATIONS
                            the number of picking stations
      -N NUM, --num NUM     the number of instances to create (default: 1)
      -C, --console         prints the instances to the console
      -d DIRECTORY, --directory DIRECTORY
                            the directory to safe the files (default:
                            generatedInstances)
      --se, --skip-existing
                            skip instance generation if destination directory
                            already exists
      --instance-dir        each instance is stored in unique directory where the
                            path is the concatenation of '<DIRECTORY>/<INSTANCE-
                            NAME>/'
      --instance-dir-suffix INSTANCE_DIR_SUFFIX
                            additional instance dir suffix, i.e., each instance is
                            stored in unique directory where the path is the
                            concatenation of '<DIRECTORY>/<INSTANCE-
                            NAME><SUFFIX>/'
      --instance-count INSTANCE_COUNT
                            each instance gets the given value as running number
                            instead of using its rank in the enumeration of clasp
      -f NAME_PREFIX, --name-prefix NAME_PREFIX
                            the name prefix that eyery file name will contain
      -v, --version         show program's version number and exit
      -t THREADS, --threads THREADS
                            run clingo with THREADS threads (default: 1)
      -w WAIT, --wait WAIT  time to wait in seconds before solving is aborted if
                            not finished yet (default: 300)
      --random              Randomize clingo's model enumeration based on the
                            flags '--rand-freq', '--sign-def', and '--seed'
      --rand-freq PERCENTAGE
                            for model randomization: the '--rand-freq=PERCENTAGE'
                            flag passed to clingo (default: 0.5)
      --sign-def DEFAULT_SIGN
                            for model randomization: the '--sign-def=DEFAULT_SIGN'
                            flag passed to clingo (default: rnd)
      --seed SEED           for model randomization: the '--seed=SEED' flag passed
                            to clingo (default: 123456789)
      --sopts, --solve-opts SOLVE_OPTS
                            options pass-through of to underlying clingo process,
                            **intended for debugging only!**
      -I, --gen-inc         use incremental instance generation; required for
                            large instances to reduce grounding size
      --im, --inc-im        for inc-mode, activate output of intermediate
                            instances (default: False)
      -V, --verbose         verbose output (default: 30)
      -D, --debug           debug output (default: 30)
      --gstats [OPT]        WARNING: FOR ANALYTICAL PURPOSE ONLY, DO NOT USE FOR PRODUCTION!
                            Shows grounding size statistics for each program part of the instance
                            generator encoding, takes optional argument OPT:
                              stats : shows the grounding size statistics (implied by default)
                              atoms : additionally shows the grounded program and output atoms & terms

    Batch mode options:
      -j JOB, --batch JOB   a batch job of multiple instance generations specified
                            by a job file; Warning: additional command line
                            parameters will be carried over as input parameters
                            for single instance generation runs, unless explicitly
                            redefined in the job file
      -c [CAT [CAT ...]], --cat [CAT [CAT ...]]
                            optional list of names (i.e., prefixes) of sub-
                            categories to create
      --su, --skip-existing-sub
                            during batch instance generation, skip those sub-
                            directories that exist; helpful to resume interrupted
                            generation jobs
      --tr, --template-relative
                            consider template paths relative to the destination
                            directory (-d) if given
      --preo, --pre-only    *only* compute instances for the configuration presets
                            instead of their variants
      --pret, --pre-too     *additionally* compute instances for the configuration
                            presets in addition to their variants

    Product constraints:
      -P PRODUCTS, --products PRODUCTS
                            the number of product kinds
      -u PRODUCT_UNITS_TOTAL, --product-units-total PRODUCT_UNITS_TOTAL
                            the total number of product units stored in the
                            warehouse
      --pusmin PUSMIN, --min-product-units-per-product-shelf PUSMIN
                            for each product an shelf it is stored on, the minimum
                            number of stored units (default: 1)
      --pusmax PUSMAX, --max-product-units-per-product-shelf PUSMAX
                            for each product and shelf it stored on, the maximum
                            number of stored units (default: 10); deactivate with
                            value < 1
      --pus PUS, --product-units-per-product-shelf PUS
                            for each product and shelf it is stored on, the exact
                            number of stored units (default: None); shorthand for
                            '--pusmin PUS --pusmax PUS'
      --prsmin MINPRS, --min-products-per-shelf MINPRS
                            the minimum number of products per shelf (default: 0)
      --prsmax MAXPRS, --max-products-per-shelf MAXPRS
                            the maximum number of products per shelf (default:
                            20); deactivate with value < 1
      --prs PRS, --products-per-shelf PRS
                            the number of products per shelf (default: None);
                            shorthand for '--prsmin PRS --prsmax PRS'
      --sprmin MINSPR, --min-shelves-per-product MINSPR
                            the maximum number of shelves that contain the same
                            product (default: 1); deactivate with value < 1
      --sprmax MAXSPR, --max-shelves-per-product MAXSPR
                            the maximum number of shelves that contain the same
                            product (default: 4); deactivate with value < 1
      --spr SPR, --shelves-per-product SPR
                            the maximum number of shelves that contain the same
                            product (default: None); shorthand for '--sprmin SPR
                            --sprmax SPR'

    Order constraints:
      -o ORDERS, --orders ORDERS
                            the number of orders
      --olmin MINOL, --min-order-lines MINOL
                            the minimum number of lines per order (default: 1)
      --olmax MAXOL, --max-order-lines MAXOL
                            the maximum number of lines per order (default: 1)
      --ol OL, --order-lines OL
                            the exact number lines per order (default: None);
                            shorthand for '--olmin OL --olmax OL'
      --oap, --order-all-products
                            Each product should at least be ordered once.

    Layout constrains:
      There are two major layout categories: *random* as default, or *highway*
      via the -H flag. Depending on the major layout type, there are further
      customization options available as follows.

    * General layout constraints:
      -R, --reachable-shelves
                            all shelves are reachable from all picking stations
                            w/o moving other shelves

    * Constraints for the *random* layout:
      --gs GAP_SIZE, --gap-size GAP_SIZE
                            the maximum size of "gaps" (i.e., blocked node
                            components) in the floor grid (default: 2)

    * Constraints for the *highway* layout:
      -H, --highway-layout  Manhattan-style street grid using highway-nodes
      -X CLUSTER_X, --cluster-x CLUSTER_X
                            for highway-layout: the size of one rectangular shelf
                            cluster in x-direction (default: 2)
      -Y CLUSTER_Y, --cluster-y CLUSTER_Y
                            for highway-layout: the size of one rectangular shelf
                            cluster in y-direction (default: 2)
      -B BELTWAY_WIDTH, --beltway-width BELTWAY_WIDTH
                            for highway layout: the width of the beltway
                            surrounding all shelf clusters (default: 1)
      --ph-pickstas PH_PICKSTAS
                            placeholder for picking stations, i.e., the number of
                            picking stations expected to be added to the instance
                            in the future; required for adequate clearance of grid
                            nodes at the top if the amount of picking stations is
                            not specified (default: 1)
      --ph-robots PH_ROBOTS
                            placeholder for robots, i.e., the number of robots
                            expected to be added to the instance in the future;
                            required for adequate clearance of grid nodes at the
                            top if the amount of robots is not specified (default:
                            1)

    Template and projection options:
      -T [TEMPLATE [TEMPLATE ...]], --template [TEMPLATE [TEMPLATE ...]]
                            every created instance will contain all atom defined
                            in base program of the template file(s) (default: []);
                            alternatively, with argument '-T -', template facts
                            can be streamed in directly from stdin
      --prj-orders          project enumeration to order-related init/2 atoms
      --prj-warehouse       project enumeration to warehouse-related init/2 atoms
      --split NUM NUM       splits instances into warehouse and order-related
                            facts; takes as arguments 1.) the number of warehouses
                            and 2.) the orders per warehouse to create, resp.

# Name Convention for Instance Files

Generated instance files are automatically named in adherence to the scheme

    x<X>_y<X>_n<N>_r<R>_s<S>_ps<PS>_pr<PR>_u<U>_o<o>_N<NI>.lp

where

- `<X>` is the maximum x-dimension
- `<Y>` is the maximum y-dimension
- `<N>` is the number of nodes
- `<R>` is the number of robots
- `<S>` is the number of shelves
- `<PS>` is the number of picking stations
- `<PR>` is the number of products
- `<U>` is the number of product units globally, i.e., total across all products
- `<O>` is the number of orders
- `<NI>` is the instance count number

Example

    x10_y10_n100_r5_s20_ps5_pr5_u48_o6_N003.lp

is an instance where

- `10` is the maximum x-dimension
- `10` is the maximum y-dimension
- `100` is the number of nodes
- `5` is the number of robots
- `20` is the number of shelves
- `5` is the number of picking stations
- `5` is the number of products
- `48` is the number of product units globally, i.e., total across all products
- `6` is the number of orders
- `3` is the instance count number


## Example Generation Calls

### Structured (Real-world-like) Instances

-   Small instance with
    - 9x6 floor grid (`x 9 -y 6`)
    - 3x2 shelf cluster dimensions (`-X 3 -Y 2`)
    - 6 shelves (`-s 6`)
    - 1 picking stations (`-p 1`)
    - 2 robots (`-r 2`)
    - highway-layout (`-H`)
    - 4 products (`-P 4`)
    - 20 product units (`-u 20`)
    - 4 orders (`-o 4`)
    - guarantee that all products are ordered at least once (`--oap`)

    via

    ``` bash
    gen -x 9 -y 6 -X 3 -Y 2 -s 6 -p 1 -r 2 -H -P 4 -u 20 -o 4 --oap
    ```

-   Medium-size instance with
    - 13x12 grid (`x13 -y 12`)
    - 5x2 shelf cluster dimensions (`-X 5 -Y 2`)
    - 30 shelves (`-s 30`)
    - 3 picking stations (`-p 3`)
    - 5 robots (`-r 5`)
    - highway-layout (`-H`)
    - 6 products (`-P 6`)
    - 32 product units (`-u 32`)
    - 8 orders (`-o 8`)
    - 3 shelves per product that hold its units (`--spr 3`)
    - 4 clingo threads (`-t 4`)

    via

    ``` bash
    gen -x 13 -y 12 -X 5 -Y 2 -s 30 -p 3 -r 5 -H -P 6 -u 32 -o 8 --spr 2 -t 4
    ```


### Random Instances

-   Small instance with
    - 10x10 grid (`x 10 -y 10`)
    - 50 shelves (`-s 50`)
    - 10 picking stations (`-p 10`)
    - 30 robots (`-r 30`)
    - 10 products (`-P 10`)
    - 100 product units (`-u 100`)
    - 8 orders (`-o 8`)
    - 4 products per shelf (`--prs 2`)
    - 4 clingo threads (`-t 4`)
    - verbose output (`-V`)
    - incremental generation (`-I`)

    via

    ``` bash
    gen -x 10 -y 10 -s 50 -p 10 -r 30 -P 10 -u 100 -o 8 --prs 2 -t 4 -V -I
    ```

-   Medium-size instance
    - 20x20 grid (`x 20 -y 20`)
    - 160 shelves (`-s 160`)
    - 20 picking stations (`-p 20`)
    - 10 robots (`-r 10`)
    - 12 products (`-P 12`)
    - 64 product units (`-u 64`)
    - 10 orders (`-o 10`)
    - 4 clingo threads (`-t 4`)
    - verbose output (`-V`)
    - incremental generation (`-I`)

    via

    ``` bash
    gen -x 20 -y 20 -s 160 -p 20 -r 10 -P 12 -u 64 -o 10 -t 4 -V -I
    ```


## Batch Generation

Instead of running the instance generator with a single configuration of parameters from the command
line, there is also support for batch generation based on a range of different configurations: batch
files are defined in [YAML](yaml.org) syntax, for example the batch
files

- [`./generator/scripts/batch/abc/structured.yml`]({{ site.asprilo_src_url }}/generator/scripts/batch/abc/structured.yml) and
- [`./generator/scripts/batch/abc/random.yml`]({{ site.asprilo_src_url }}/generator/scripts/batch/abc/random.yml)

describe a set of structured and random instances, respectively, suited for domain A-C. The generator can process them via the `--batch` command line option, e.g.

    gen --batch ./generator/scripts/batch/abc/structured.yml -I -t 4 -V

### Batch File Format

-   A valid batch file always contains exactly two top-level dictionaries:

    - `global_settings` describing configuration parameters that should be used globally, i.e., for each instance generation job
    - `run_configs` describing the generation jobs represented as collection of different
            configurations

-   Basic Job Definition:

    - Within the `run_configs` tree, a user can represent a single instance generation job by a
      dictionary, that is not only an ancestor of `run_configs` but also all its predecessors must
      be dictionaries; in the resulting instance set, the paths from `run_configs` to job dictionaries are translated
      correspondingly into directory trees in the file system
    - Further, a job dictionary must have a child directory with the reserved name `args` that, in
      turn, specifies the job's configuration parameters in a dictionary
    - Each job dictionary, that is, their parameters specified by their `args` child dictionary will
      be processed as single instance generation job by the generation

-   Recursive Job Definition:

    - Optionally, a job dictionary may also contain a child or ancestor dictionary that in turn
      define jobs, i.e., contain an `args` child dictionary; That is, down-stream job dictionaries
      inherit the configuration parameters from their ancestor job dictionaries
    - Eventually, only those job dictionaries which have no ancestor job dictionaries are executed
      by the instance generator
