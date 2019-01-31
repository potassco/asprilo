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

**asprilo** is an benchmarking framework to study typical scenarios in intra-logistics and warehouse
automation with multiple mobile robots. It offers a concise specification of this problem domain
accompanied by a set of tools to generate benchmark instances, verify plans, as well as visualize
both instances and plans. Due to the diverse and complex nature of this domain, asprilo offers an
ideal test bed not only for modern industrial scenarios but complex dynamic problems in
general. Although, the implementation of asprilo relies on [answer set programming
(ASP)](https://en.wikipedia.org/wiki/Answer_set_programming) and Python, it also supports any other
approach that complies with its fact-based I/O interface.

| "Full Warehouse Domain" (A-Domain)  | "Movement-Only Domain" (M-Domain) |
|:-:|:-:|
[![](https://img.youtube.com/vi/ifYKHIvdnjw/0.jpg)](https://www.youtube.com/watch?v=ifYKHIvdnjw) | [![](https://img.youtube.com/vi/GHRwpWzL0j8/0.jpg)](https://www.youtube.com/watch?v=GHRwpWzL0j8)

(*Click images for video playback*)

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

# Publications

1. Gebser, M., Obermeier, P., Otto, T., Schaub, T., Sabuncu, O., Nguyen, V., & Son, T. C. (2018). Experimenting with robotic intra-logistics domains. *CoRR*, abs/1804.10247. [[pdf](https://www.cs.uni-potsdam.de/wv/publications/DBLP_journals/corr/abs-1804-10247.pdf)] [[bib](https://www.cs.uni-potsdam.de/wv/publications/DBLP_journals/corr/abs-1804-10247.html)]
2. Gebser, M., Obermeier, P., Otto, T., Schaub, T., Sabuncu, O., Nguyen, V., & Son, T. C. (2018). Experimenting with robotic intra-logistics domains. *TPLP*, 18(3-4), 502–519. [[bib](https://www.cs.uni-potsdam.de/wv/publications/DBLP_journals/tplp/GebserOOS18.html)]
3. Nguyen, V., Obermeier, P., Son, T. C., Schaub, T., & Yeoh, W. (2017). Generalized Target Assignment and Path Finding Using Answer Set Programming. In *IJCAI* (pp. 1216–1223). ijcai.org. [[pdf](https://www.cs.uni-potsdam.de/wv/publications/DBLP_conf/ijcai/NguyenOSS017.pdf)] [[bib](https://www.cs.uni-potsdam.de/wv/publications/DBLP_conf/ijcai/NguyenOSS017.html)]
