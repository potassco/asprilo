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

# Requirements

The instance generator requires ![PyYAML](https://github.com/yaml/pyyaml), e.g. install via

    pip install pyyaml

# Usage

The script `./generator/ig` provides an instance generator with various configuration options, for
a detailed list and description run

    ig -h


## Example Instance Generations

### Real-world-like Instances

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
    ig -x 9 -y 6 -X 3 -Y 2 -s 6 -p 1 -r 2 -H -P 4 -u 20 -o 4 --oap
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
    - guarantee that all products are ordered at least once (`--oap`)

    via

    ``` bash
    ig -x 13 -y 12 -X 5 -Y 2 -s 30 -p 3 -r 5 -H -P 6 -u 32 -o 8 --oap
    ```


### Random Instances

-   Small instance with
    - 10x10 grid (`x 10 -y 10`)
    - 50 shelves (`-s 50`)
    - 10 picking stations (`-p 10`)
    - 30 robots (`-r 30`)
    - 10 products (`-P 10`)
    - 40 product units (`-u 40`)
    - 8 orders (`-o 8`)
    - guarantee that all products are ordered at least once (`--oap`)

    via

    ``` bash
    ig -x 10 -y 10 -s 50 -p 10 -r 30 -P 10 -u 40 -o 8 --oap
    ```

-   Medium-size instance containing gaps with
    - 20x20 grid (`x 20 -y 20`)
    - 360 nodes (`-n 360`) and hence 40 gaps
    - 160 shelves (`-s 160`)
    - 20 picking stations (`-p 20`)
    - 10 robots (`-r 10`)
    - 12 products (`-P 12`)
    - 64 product units (`-u 64`)
    - 10 orders (`-o 10`)
    - guarantee that all products are ordered at least once (`--oap`)

    via

    ``` bash
    ig -x 20 -y 20 -n 360 -s 160 -p 20 -r 10 -P 12 -u 64 -o 10 --oap
    ```

### Near-Uniform sampling with --xor
To generate near-uniform samples from either real-world-like or random instances is necessary to add the flag `--xor XOR`. The value XOR is a positive integer number referring the number of XOR constraints to be added during the solving stage.

A starting value for XOR would be 0, meaning an automatic calculation of the number of constraints and this value is obtained based on the total number of init/2 atoms.

Is possible to add more or fewer constraints by changing the XOR value. Adding more constraints may result in a more uniform sampling but also can be more susceptible to result in unsatisfiable solution caused by inconsistencies in two or more constraints. Also, adding more constraints may hinder the solving performance. Adding fewer constraints will perform better but can return a weak sampling and not close to near-uniformity.

A real-world-like small instance can be executed via

    ``` bash
    ig -x 9 -y 6 -X 3 -Y 2 -s 6 -p 1 -r 2 -H --xor 0
    ```

## Batch Generation (TODO)

Instead of running the instance generator with a single configuration via command line parameters,
there is also support for the batch generation of instances based on a range of different
configurations specified in a batch file. Batch files are defined in ![YAML](yaml.org) syntax, for
instance, the referential benchmark set is created via the batch files

- [`./generator/scripts/batch/referential-standard.yml`](../generator/scripts/batch/referential-standard.yml) and
- [`./generator/scripts/batch/referential-random.yml`](../generator/scripts/batch/referential-random.yml)

for standard and random instances, respectively. Moreover, a valid batch file always contains exactly two top-level dictionaries:

- `global_settings` describing configuration parameters that should be used globally, i.e., for each instance generation job
- `run_configs` describing the generation jobs represented as collection of different configurations
