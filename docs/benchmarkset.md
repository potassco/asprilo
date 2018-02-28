# About

This is the description of the pre-generated benchmark instance sets for ASPRILO.

# Instance Sets

The latest [ASPRILO release](https://github.com/potassco/asprilo/releases) provides a set of
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
            ├── 2x3x5
            │   └── 100sc
            └── 4x5x8
                └── 100sc


The instances are partitioned into two parts:

-   `./abc`:
    - A structured instance set suited for domain A,B and C
    - Created by the [instance generator](generator.md) with batch file
      [`./generator/scripts/batch/abc/structured.yml`](../generator/scripts/batch/abc/structured.yml)

-   `./moo`:
    - A structured instance set primarily designed for domain M but by definition also compatible
      with domain A, B, C
    - Created by the [instance generator](generator.md) with batch file
      [`./generator/scripts/batch/moo/structured.yml`](../generator/scripts/batch/moo/structured.yml)
