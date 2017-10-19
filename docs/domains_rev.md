---
layout: page
title: domains revised
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# Revised Domain Hierarchy


## Default Problem Domain (DEF)

Identical to the default domain in the specification.

## Disregard of Product Quantities (DPQ)

Identical to DPQ domain in the specification

## Simultaneous Deliveries (SID)

Identical to IDC domain in the specification

## Movements Only (MOO)

This is a TAPF-syle simplification of the default domain in the sense that:

- The only action that robots can perform is move, i.e., there are no pickup, putdown or delivery
  actions in plans.
- Shelves are fixed in place
- There is a one-to-one correspondence between shelves and products
- The number of orders and robots is identical
- An order contains exactly one order line
- Goal: An *order line* is fulfilled if a robot is located under the shelf that contains
  the order line's requested product at the end

<!-- -   Puristic TAPF: -->
<!-- -   TAPF w/ multiple checkpoints: -->
<!--     - An order may contain more than one order line as per usual -->
