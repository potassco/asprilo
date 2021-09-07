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

**asprilo** is a benchmarking framework to study typical scenarios in intra-logistics and warehouse
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

- Gebser, M., Obermeier, P., Otto, T., Schaub, T., Sabuncu, O., Nguyen, V., & Son, T. C. (2018). [Experimenting with robotic intra-logistics domains]({{ site.publicationurl }}//#DBLP:journals/corr/abs-1804-10247). *CoRR*, abs/1804.10247. [[Experiments]({{ site.page.asprilo_web_url }}/experiments/#evaluation-2018-02)]
- Gebser, M., Obermeier, P., Otto, T., Schaub, T., Sabuncu, O., Nguyen, V., & Son, T. C. (2018). [Experimenting with robotic intra-logistics domains]({{ site.publicationurl }}//#DBLP:journals/tplp/GebserOOS18). *TPLP*, 18(3-4), 502–519. [[Experiments]({{ site.page.asprilo_web_url }}/experiments/#evaluation-2018-02)]
- Nguyen, V., Obermeier, P., Son, T. C., Schaub, T., & Yeoh, W. (2017). [Generalized Target Assignment and Path Finding Using Answer Set Programming]({{ site.publicationurl }}//#DBLP:conf/ijcai/NguyenOSS017). In *IJCAI* (pp. 1216–1223). ijcai.org.
