---
layout: page
title: checker
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the user manual of the solution checker of [ASPRILO](index.md).


# Encoding Structure

The checker&rsquo;s encoding is compartmentalized into several parts with respect to

1.  the problem domain, i.e., all encodings related to a domain `DOMAIN` are stored in a separate
    directory `./checker/encodings/DOMAIN/`, .e.g. `./checker/encodings/default/` for the [default
    domain](specification.md)

2.  the initial environmental state and the general law of inertia stored in
    `./checker/encodings/DOMAIN/init.lp`, .e.g. `./checker/encodings/default/` for the default
    domain

3.  <a id="action-laws"></a>the types of action laws to verify, that is,
    -   *action preconditions* and *related inertial abnormals* stored in
        `./checker/encodings/DOMAIN/ACTION` for each action type `ACTION`, e.g. for the default
        domain&rsquo;s action types `move`, `pickup`, `putdown` and `deliver`, the respective
        encodings are

            ./checker/encodings/default/action-move.lp
            ./checker/encodings/default/action-pickup.lp
            ./checker/encodings/default/action-putdown.lp
            ./checker/encodings/default/action-deliver.lp

    -   *static laws* stored in `./checker/encodings/DOMAIN/static.lp`,
        e.g. `./checker/encodings/default/static.lp` for the default domain

4.  the goal condition stored in `./checker/encodings/DOMAIN/goal.lp`, .e.g. for the default,
    `./checker/encodings/default/`

For each `DOMAIN`, all [action law encodings](#action-laws) are then integrated via `#include` directives in the
encoding `./checker/encodings/DOMAIN/checker.lp`, .e.g.  `./checker/encodings/default/checker.lp`
for the default domain.


# Currently Supported Domains

At present we support the following problem domains:

-   the [default domain](specification.md)
    - checker encodings at `./checker/encodings/default/`
-   the default domain in conjunction with the ['disregard of product quantities'
    (DPQ)](specification.md) modification
    - checker encodings at `./checker/encodings/dpq`


# How To Use

In general, within a problem domain `DOMAIN`, to check a plan file `PLAN` for an instance file
`INSTANCE` run

    clingo ./checker/encodings/DOMAIN/checker.lp INSTANCE PLAN

Any inconsistencies will then be indicated by `err/3` atoms in the answer set, which are defined
in the [checker's encoding files](#-encoding-structure). Moreover, `err/3` facts adhere to the format

    err(FileID, CheckID, Parameters)

where

1. `FileID` indicates the encoding file in which the yielded `err/3` atom is defined
2. `CheckID` indicates the specific &rsquo;check&rsquo;, i.e., a rule that defines the `err/3` atom
3. `Parameters` the relevant term parameters in the body of the rule

E.g., for the default domain and instance `./examples/default/instance.asp`, the (invalid) plan
`./examples/default/wrong_outcome.txt` can be checked via

    clingo ./checker/encodings/default/checker.lp ./examples/default/instance.asp \
           ./examples/default/wrong_outcome.txt --out-ifs="\n"|grep err

which yields:

    err(goal,unfilledOrder,(3,3,1,11))
    err(goal,unfilledOrder,(3,2,1,11))

Those `err/3` facts are defined in `./checker/encodings/default/goal` by rule

    err(goal, unfilledOrder, (O, P, Q, H)) :- holds(object(order, O), value(line, (P, Q)), H);
                                              horizon(H).

that indicates, that there are still unfulfilled orders at the end of the plan. Specifically,

- `err(goal,unfilledOrder,(3,3,1,11))` indicates that order `O = 3` still requires `Q = 1` units of
  product `P = 3`.
- `err(goal,unfilledOrder,(3,2,1,11))` indicates that order `O = 3` still requires `Q = 1` units of
  product `P = 2`.
