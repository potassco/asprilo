## Viz_speedup

This branch is dedicated to the removal of some bottlenecks in the asprilo-visualizer, which currently scales poorly with instance size.
Some features might be lost when recoding larger parts of the program and may be reimplemented later.

#### WIP/completed (might still be subject to change)

- new internal data model for instance model
- new data model for visualizer item
- new data model for ModelView Widget
- new parsing module

#### To do /currently planned

- make atom types and actions configurable per YAML
- untangle references and dependencies
- introduce stricter type checking (where applicable)
- clean up imports
- error handling

# ASPRILO [![Github Release](https://img.shields.io/github/release/potassco/asprilo/all.svg)](https://github.com/potassco/asprilo/releases)

## About

This is the source tree of **ASPRILO**, an intra-logistics benchmark suite for answer set
programming. For further details, please consult the documentation on our website at
<https://asprilo.github.io/>.

## Directory Structure

- `./docs/` contains the documentation sources
- `./checker/` contains the instance generator sources
- `./generator/` contains the instance generator sources
- `./visualizer/` contains the instance visualizer sources
