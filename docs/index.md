---
layout: default
title: index
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# What is *asprilo*?

**asprilo** is a benchmark suite for [answer set programming
(ASP)](https://en.wikipedia.org/wiki/Answer_set_programming), based on typical scenarios in
intra-logistics and warehouse automation with multiple mobile robots. Specifically, the diverse and
complex nature of those settings makes them an ideal test bed for methods and technologies in
ASP. Beyond that, asprilo also supports any other solving approach that complies with its I/O
interface.

<iframe width="49%" height="315" src="https://www.youtube.com/embed/ifYKHIvdnjw" frameborder="0" allowfullscreen align="left"></iframe>
<iframe width="49%" height="315" src="https://www.youtube.com/embed/GHRwpWzL0j8" frameborder="0" allowfullscreen align="right"></iframe>


# Key Components

asprilo provides the following essential components:

-   A detailed [problem specification](specification.md), stipulating the problem domain including variations as well as
    the technical I/O format
-   A benchmark toolkit comprised by
    - [instance generator](generator.md) that supports a plethora of customization options
    - [solution checker](checker.md) to check plans for all supported problem domains
    - [visualizer](visualizer.md) to display instances and plans
    - [pre-generated set of test instances](benchmarkset.md)

# Development

The source code of the project is available at <https://github.com/potassco/asprilo>

# Experiments

Information about our conducted experiments with asprilo can be found [here](experiments.md).
