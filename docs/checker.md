---
layout: page
title: Checker
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the user manual of the solution checker of [asprilo](index.md).


# Encoding Structure

The checker's encoding is compartmentalized into several parts with respect to

1.  the problem domain, i.e., all encodings related to a domain `DOMAIN` are stored in a separate
    directory `./checker/encodings/DOMAIN/`, .e.g. `./checker/encodings/a/` for the [A
    domain](specification.md)

2.  the initial environmental state and the general law of inertia stored in
    `./checker/encodings/DOMAIN/init.lp`, .e.g. `./checker/encodings/a/init.lp` for the A
    domain

3.  <a id="action-laws"></a>the types of action laws to verify, that is,
    -   *action preconditions* and *related inertial abnormals* stored in
        `./checker/encodings/DOMAIN/ACTION` for each action type `ACTION`, e.g. for the A
        domain&rsquo;s action types `move`, `pickup`, `putdown` and `deliver`, the respective
        encodings are

            ./checker/encodings/a/action-move.lp
            ./checker/encodings/a/action-pickup.lp
            ./checker/encodings/a/action-putdown.lp
            ./checker/encodings/a/action-deliver.lp

    -   *static laws* stored in `./checker/encodings/DOMAIN/static.lp`,
        e.g. `./checker/encodings/a/static.lp` for the A domain

4.  the goal condition stored in `./checker/encodings/DOMAIN/goal.lp`, .e.g. for the A,
    `./checker/encodings/a/goal.lp`

For each `DOMAIN`, all [action law encodings](#action-laws) are then integrated via `#include` directives in the
encoding `./checker/encodings/DOMAIN/checker.lp`, .e.g.  `./checker/encodings/a/checker.lp`
for the A domain.


# How To Use

Within a problem domain `DOMAIN`, to check a plan file `PLAN` for an instance file
`INSTANCE` run

    clingo ./checker/encodings/DOMAIN/checker.lp INSTANCE PLAN

Any inconsistencies will then be indicated by `err/3` atoms in the answer set, which are defined
in the [checker's encoding files](#-encoding-structure). Moreover, `err/3` facts adhere to the format

    err(FileID, CheckID, Parameters)

where

1. `FileID` indicates the encoding file in which the yielded `err/3` atom is defined
2. `CheckID` indicates the specific &rsquo;check&rsquo;, i.e., a rule that defines the `err/3` atom
3. `Parameters` the relevant term parameters in the body of the rule

E.g., for the A domain and instance `./examples/a/instance.asp`, the (invalid) plan
`./examples/a/wrong_outcome.txt` can be checked via

    clingo ./checker/encodings/a/checker.lp ./examples/a/small/x11_y6_n66_r3_s12_ps2_pr5_u50_o3_N001.lp \
           ./examples/a/small/wrong_outcome.txt --out-ifs="\n"|grep err

which yields:

    err(deliver,orderAmount,(1,23))
    err(deliver,shelfAmount,(1,23))
    err(goal,unfilledOrder,(1,2,1,29))

Those `err/3` facts are defined in `./checker/encodings/a/action-deliver.lp` and
`./checker/encodings/a/goal.lp` by rules:

    err(deliver, orderAmount, (R, T)) :- occurs(object(robot, R), action(deliver, (O, P, Q)), T);
                                         holds( object(order, O), value( line,    (P, RQ)  ), T-1);
                                         Q > RQ.


    err(deliver, shelfAmount, (R, T)) :- occurs(object(robot, R),   action(deliver, (O, P, Q)), T);
                                         holds( object(robot, R),   value(carries,  S        ), T-1);
                                         holds( object(product, P), value(on,     (S, SQ)  )  , T-1);
                                         Q > SQ.


    err(goal, unfilledOrder, (O, P, Q, H)) :- holds(object(order, O), value(line, (P, Q)), H);
                                              horizon(H).

that indicate that the plan contains inconsistencies with respect to the domain definition. Specifically,

- `err(deliver,orderAmount,(1,23))` indicates that robot `1` delivered more products than requested
  at time step `23`
- `err(deliver,shelfAmount,(1,23))` indicates that robot `1` removed from the shelf it carries more
  than the available amount of a product at time step `23`
- `err(goal,unfilledOrder,(1,2,1,29))` indicates that order `1` still requires `1` units of product
  `2` at the final time step `29`.
