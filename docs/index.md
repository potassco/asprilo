---
layout: page
title: index
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# What is ASPRILO?

**ASPRILO** is a benchmark suite for [answer set programming (ASP)](https://en.wikipedia.org/wiki/Answer_set_programming), based on typical scenarios in
intra-logistics and warehouse automation with multiple mobile robots. Specifically, the diverse
and complex nature of those settings makes them an ideal test bed for methods and technologies in
ASP. Beyond that, ASPRILO also supports any other solving approach that complies with its I/O
interface.


# Key Components

Essentially, ASPRILO provides the following components:

-   A detailed [problem specification](specification.md), stipulating the problem domain including variations as well as
    the technical I/O format
-   A benchmark toolkit comprised by
    - [instance generator](generator.md) that supports a plethora of customization options
    - [solution checker](checker.md) to check plans for all supported problem domains
    - [visualizer](visualizer.md) to display instances and plans
    - [referential set of test instances](benchmarkset.md)


# Development

The source code of the project is available at <https://github.com/potassco/asprilo>
