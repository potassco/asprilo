---
layout: page
title: Specification
output:
    html_document:
        toc: true
        toc_depth: 3
        toc_float: true
---

# About

This is the problem specification of [asprilo](index.md). Subsequently, we

- gradually specify the problem domain in different variations, beginning with the default scope
- stipulate the technical instance and plan format
- provide a example instance and plan


# Domain A: The General Problem<a id="cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b"></a>

asprilo's benchmark scenario is inspired by intra-logistics and warehouse automation systems based
on multiple mobile robots and shelves. Its main goal is order fulfilment in a warehouse, i.e., order
picking and sortation for a given set of product orders. Specifically, the warehouse floor is laid
out as a 2-dimensional grid. Products are stored in shelves, each located in a single grid
node. Mobile robots can move and navigate through the warehouse along the grid. Moreover, they can
carry and relocate shelves, as well as bring them to picking stations to deliver products. Customer
orders are all provided at the start, each assigned to a picking station. An order is fulfilled if
all its requested product units are delivered to its assigned picking station. The overall goal is
hence to provide a plan in form of a sequence of sets of robot actions such that all orders will be
filled. In other words, the plan should be based off a discrete time signal and each robot may
perform a single action per time point, i.e., robots generally act concurrently. In the following,
we provide a more detailed overview of the *key components* of the problem.


## Warehouse Floor Layout<a id="cid-7e4e0e03-fa41-4809-8f83-b8e6a19986d7"></a>

The warehouse floor is typically laid out as a *grid*, i.e.,

- a 2-dimensional *grid graph*; or
- a *partial* 2D grid graph (i.e., subgraph of a grid) to resemble more complex shapes: e.g. several
  rectangles connected by smaller passages, a cross-shaped grid, etc.

The grid may also contain special *highway nodes* that must never be occupied by a parked shelf.
Besides, we refer to grid nodes also as *storage nodes* if they are neither occupied by a picking
station nor are a highway node.


## Products<a id="org7835632"></a>

A *product* is a type of physical good that owns an unique identifier (e.g. part number, universal
product code). Products are typically handled in certain quantities, i.e., number of *units*,
e.g. 20 units of the product with unique identifier '7324552'.


## Shelves<a id="org5668d0c"></a>

*Shelves* store product units in limited quantities. Further, they occupy exactly one grid node when
parked.


## Robots<a id="org2f92cab"></a>

Mobile *robots* can freely move along the grid (even under shelves) as long as the grid node is not
already occupied by another robot.  Further, they can *pick up* a shelf when under it, *carry* it
while moving, and *put it down* eventually. While carrying a shelf, their movement is restricted to
fields clear of other shelves and robots. At a picking station, robots can *deliver* product units
from their shelf to the totes of the station. Moreover, robots occupy exactly one grid node at each
time point.


## Picking Stations<a id="org0a65cc2"></a>

Picking stations store product units requested by orders for further processing. Further, picking stations consume one
grid node, and a robot can occupy the same node as picking station in order to deliver product
units to it.


## Orders<a id="org9eaff1c"></a>

*Orders* are sets of *order lines*, i.e., a set of requests for products in certain quantities,
e.g. an order with 3 lines:

- 3 pens
- 2 notebooks
- 1 file folder

All orders are known initially (instead of arriving over time) and have a picking station assigned
to them. Further, an order contains at most one order line per product. An order line is *fulfilled*
if all its requested product units are delivered to the picking station assigned to the order. An
order is fulfilled if all its order lines are fulfilled.


# Key Characteristics of Instances<a id="org9cfe104"></a>

Here, we present the characteristics (without any claim of completeness) that we consider relevant
to distinguish problem instances. This is a preliminary step for our subsequent problem
classification which is, in turn, implemented by our [instance generator](manual.md). Instance characteristics
can be further divided up into aspects related to the instance's warehouse and set of orders,
respectively. Moreover, instance characteristics depend on the scope of the problem domain, and
the order set properties also depend on the warehouse characteristics.  In the following, we list
our instance characteristics for the default problem, and later expand on those in connection with
[problem domain modifications](#cid-bbacc203-29c4-489f-8661-95cf4b599fdd).


## Warehouse Characteristics<a id="cid-1ff2ac2f-a6f1-4ddd-b0f0-5e3d2af2d4d0"></a>

Besides the problem scope, the key aspects of the warehouse boil down to its floor plan layout for
which we can identify the following criteria.


### Floor Topology Type<a id="cid-b3c44568-d34b-4c4d-bac0-a1483b4a99e8"></a>

For the floor topology, we distinguish between two basic graph types:

- grid graph (default)
- general two-dimensional graph<sup><a id="fnr.1" class="footref" href="#fn.1">1</a></sup>


### Floor Topology Layout<a id="org8cea9ca"></a>

In case the [floor topology type](#cid-b3c44568-d34b-4c4d-bac0-a1483b4a99e8) is a grid, the topology
layout is a rectangular grid graph by default. Further, we can consider more complex grid shapes,
e.g. several rectangles connected by smaller corridors, a cross-shaped grid, a T-shaped grid, etc.

If the topology type is a general graph, we do not regard its layout at present.


### Structured Layout of Highway Nodes, Shelves and Picking Stations<a id="cid-d70674e1-8273-4abb-8ebf-b05f261c621a"></a>

Here, we distinguish whether highway nodes, shelves and picking stations are placed randomly on the
grid or if a distinct pattern for the interiors layout is employed. That is, a most typical
pattern (see Fig. [224](#orge332373)) for rectangular warehouse grids is as follows:

-   "Manhattan-style" placement of shelves and highway nodes, i.e.
    - shelves are grouped into rectangular storage areas with size in y-dimension fixed to 2 grid nodes
    - storage areas are aligned as rows and columns on the grid
    - all storage areas are encompassed by highway nodes
-   picking stations are evenly distributed at the top row of the grid;
-   robots are initially parked in the lowest row of the grid, filling up the grid nodes from the left;

In the following, we refer to this pattern as *structured layout*.

**Storage Zones Characteristics**: When employing the structured layout, we also consider the number of rows and columns formed by storage zones
as well as the storage zone's size (i.e., occupied grid nodes) in x-dimension.


### Quantities of Interior Objects<a id="orgdf94892"></a>

We consider the quantities of interior objects, i.e., the number of

- highway nodes
- shelves
- picking stations
- robots


### Reachability of Shelves<a id="org3a09c86"></a>

A shelf is *reachable* if it can be carried to each picking station without moving other shelves
to clear path. A warehouse fulfills the *shelf-reachability* criterion if all shelves are
reachable.


### Floor Size<a id="orgfdb512c"></a>

We consider the floor size in terms of number of grid nodes. Naturally, in the case that the floor
is a regular grid (instead of a partial one), it suffices to specify the x- and y-dimensions of the
grid to entail the number of grid nodes.


### Ratio Between The Number of Shelves and Storage Nodes<a id="orgeb55f10"></a><sup><a id="fnr.1.100" class="footref" href="#fn.1">1</a></sup>

We consider the floored ratio between the number of shelves an the storage nodes in the warehouse.


## Order Set Characteristics<a id="cid-119945ff-c477-4214-98fd-a3078f9bf457"></a>

For order sets, we identified the following key aspects.


### Number of Orders<a id="org5d22606"></a>

We consider the total of number of orders posed by the instance.


### Minimum, Maximum and Average Number of Order Lines per Order<a id="orgb6f3977"></a>

We consider the minimum, maximum and floored average number of lines per order.


# Problem Domain Simplifications<a id="cid-bbacc203-29c4-489f-8661-95cf4b599fdd"></a>

For our general [domain A](#cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b), we envision various
simplification. We will subsequently describe each by stating the changes in comparison to the
default problem.

## Domain B: Disregard of Product Quantities<a id="cid-49448523-5e9b-4ed2-ac1a-6754d838b85c"></a>

This is a simplification of [domain A](#cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b) in sense that we
completely ignore product quantities. With that, a shelf at a picking station can fill an order if
it holds the required product.


## Domain C: Simultaneous Deliveries<a id="cid-f8d8f6b9-771a-4b1d-a20d-1ce03f96086b"></a>

This is a simplification of [domain B](#cid-49448523-5e9b-4ed2-ac1a-6754d838b85c) in the sense that
for a robot at a picking station, all deliveries can be processed in parallel and within a single
time step.


## Domain M: Movements Only<a id="cid-8dcd778b-8504-449d-9811-39ec61c50cbb"></a>

This is a exhaustive simplification of [domain A](#cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b) in
the sense the only action that robots can perform is move, i.e., there are no pickup, putdown or
delivery actions in plans. Further, the following constraints apply:

- the number of robots orders is identical
- the number of shelves and products is identical
- for each product, there is globally only one unit stored on a single shelf
- each order has exactly one order line that requests exactly one unit of a product
- there are no tow orders that request the same product

An order line is fulfilled if a robot is located under the shelf that contains the order
line's requested product at the end of the plan execution.

### Domain Md: Destinations for Domain M<a id="md"></a>

The domain Md provides an alternative view on the [domain M](#cid-8dcd778b-8504-449d-9811-39ec61c50cbb)
to more naturally state [*Multi-Agent Path Finding* (*MAPF*)](http://mapf.info/) instances within the asprilo framework.
That is, although semantically equivalent to [M](#cid-8dcd778b-8504-449d-9811-39ec61c50cbb), domain Md
allows to explicitly state robot *destinations* as objects of an instance, in contrast.
Moreover, in M,
a destination at the coordinates (x,y) is implicitly represented by a singleton order requesting a product.
The latter is additionally expected to be exclusively stored (in single quantity) on a shelf which is located at the same coordinates (x,y).
In comparison,
within an Md instance,
we can state the same destination directly as an object of type *destination* located at (x,y).
A plan solves an Md instance if every destination is occupied by a robot at the end.
This is equivalent to the goal of M which expects that each shelf holding a requested product shares its location with a robot at the plan's end.

Existing instances in M can be translated to Md format by augmenting (or replacing) the related orders, products and shelves with
the corresponding destination objects by applying the rule in encoding `./misc/augment-m-to-md.lp`
(or via the show statements in encoding `./misc/convert-m-to-md.lp`).
Analogously, for the opposite augmentation (conversion) from Md to M,
use encoding `./misc/augment-md-to-m.lp` (`./misc/convert-md-to-m.lp`).
For convenience, there is also a augmentation/conversion bash script `./misc/convert-md.sh`:

``` bash
Usage: convert-md.sh --m2md|--md2m|--am2md|--amd2m INSTANCE_FILE
  --m2md:  M to Md conversion
  --m2md:  Md to M conversion
  --am2md: M to Md augmentation
  --amd2m: Md to M augmentation
```

*Limited Tools Support*: at present, the visualizer and checker only support Md instances that were created by augmentation of an M instance.

# Input Format<a id="org46f96aa"></a>


## General Concepts: Object-Types and Attributes<a id="cid-f23fad45-7955-4f07-87ff-5370456e374b"></a>

At first, we need to agree on a general encoding scheme for instances. To that end, we introduce
the expected [object types](#cid-c06c73df-12c0-4fd6-977a-8f1ad64309be) with their attributes.


### Object-Types<a id="cid-c06c73df-12c0-4fd6-977a-8f1ad64309be"></a>

For the technical specification of problem instances, we first need to identify the relevant
*objects-types*. Specifically, an object-type represents a subset of the objects in the problem
domain. Additionally, it defines a set of *attributes* common to its objects. Further, applicable
object-types and attributes may vary depending on the problem scope. For example, we determine the
following object-types for [domain A](#cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b):

- `grid-node` with attribute `at`
- `robot` with attribute `at`
- `shelf` with attribute `at`
- `product` with attribute `on`
- `order` with attributes `line` and `pickingStation`
- `pickingStation` with attribute `at`

The complete list of [expected object types and their attributes](#cid-c279ce9c-c2ab-4e3f-9ec3-df2dd3a38188) is given below.


### Object Definitions<a id="cid-045df828-ed63-4a81-aa62-eba5c612e9f1"></a>

All instance data is represented as `init/2` facts of the format

    init(object(<object-type>, <object-id>), value(<attribute>, <value>)).

where

-   function `object` refers to an object by its type `<object-type>` and relative identifier
    `<object-id>`, e.g. `object(robot, 34)` for a robot with ID 34
-   function `value` specifies that the object's attribute `<attribute>` has value `<value>` e.g.

        init(object(robot, 34), value(at, (2,3))).

    states that the robot 34 is at x/y-location (2,3).


## Expected Object Types and Attributes<a id="cid-c279ce9c-c2ab-4e3f-9ec3-df2dd3a38188"></a>


### Warehouse Floor (Grid Topology)<a id="org3197795"></a>

In case the [floor topology type](#cid-b3c44568-d34b-4c4d-bac0-a1483b4a99e8) is a grid, the [warehouse floor](specification.md) uses exclusively **either**
object-type `grid` or objec-type `node` for its specification.

1.  Specified by Dimensions (`grid`)

    -   For the simple case that the warehouse is a (regular) grid, i.e., all nodes of the grid can be
        occupied by robots and shelves, it suffices to state the grid's x,y-dimension via attribute
        `xsize` and `ysize`, e.g.

            init(object(grid,1), value(xsize, 45)).
            init(object(grid,1), value(ysize, 35)).

        states that the x,y-dimensions are 45 and 35.

2.  Specified by Nodes (`node`)

    -   For the more general case that warehouse is a partial grid, i.e., only specific nodes
        of a warehouse grid can be occupied by robots and shelves, each of those nodes has to be
        explicitly stated via attribute `at`, e.g.

            init(object(node, 1), value(at, (1,5))).
            init(object(node, 2), value(at, (2,5))).

        states that there exist grid nodes 1 and 2 at coordinates (1,5) and (2,5), resp.
    -   Remark: in the problem encoding, `node` facts can be seen as generalization of `grid` in the
        sense that `grid` facts can always be translated to corresponding `node` facts.


### Robots<a id="org11e6b31"></a>

[Robots](#org2f92cab) use object-type `robot` for their specification. Their attributes are defined depending
on the problem domain scope as follows:

-   Related to All Domains:

    -   The grid position of a robot is indicated by attribute `at`, e.g.

            init(object(robot, 1), value(at, (2,3))).

        states that robot 1 is at location (2,3).

-   Related to All Domains Except For Domain M:

    -   A situation where a robot initially carries a shelf is indicated by attribute ~carries, e.g.

            init(object(robot, 2), value(carries, 5)).

        states that robot 2 is carrying shelf 5.


### Shelves<a id="org7a787ee"></a>

[Shelves](#org5668d0c) use object-type `shelf` for their specification.

-   Related to All Domains:

    -   The grid position of a shelf is indicated by attribute `at`, e.g.

            init(object(shelf, 1), value(at, (2,3))).

        states that shelf 1 is at location (2,3).


### Products<a id="orgd712db6"></a>

[Products](#org7835632) use object-type `product` for their specification.

-   Related to All Domains:

    -   A shelf on which a product is stored on is indicated by attribute `on`, e.g.,

            init(object(product, 45), value(on, (5, 280)).

        states that 280 units of product 45 are on shelf 5.

-   Related to [Domain B](#cid-49448523-5e9b-4ed2-ac1a-6754d838b85c) and [Domain C](#cid-f8d8f6b9-771a-4b1d-a20d-1ce03f96086b)

    -   In case product quantities are ignored, the value of `on` is a single integer indicating the
        shelf, e.g.

            init(object(product, 45), value(on, 5).

        states that product 45 is on shelf 5 in unlimited quantity.


### Orders<a id="org6bda5e4"></a>

[Orders](#org9eaff1c) use object-type `order` for their specification.

-   Related to All Domains:

    -   Lines of an order, i.e., requests of products in a certain quantity, are indicated by
        attribute `line`, e.g.,

            init(object(order, 7), value(line, (467, 2))).
            init(object(order, 7), value(line, (77, 12))).

        states that order 7 requests 2 units of product 467, and 12 units of product 77.

-   Related to All Domains Except for Domain M:

    -   The picking station of an order is indicated by attribute `pickingStation`, e.g.

            init(object(order, 7), value(pickingStation, 4).

        states that order 7 is assigned to picking station 4.


### Picking Stations<a id="orgbc6f688"></a>

[Picking stations](#org0a65cc2) use object-type `pickingStation` for their specification.

-   Related to All Domains:

    -   The grid position of a picking station is indicated by attribute `at`, e.g.

            init(object(pickingStation, 1), value(at, (2,3))).

        states that pickingStation 1 is at location (2,3).

### Destinations (for [domain Md](#md) only!)<a id="type-dest"></a>

[Destinations](#md) use object-type `dest` for their specification.

-   Exclusive to domain [Md](#md):
    -   The grid position of a destination is indicated by attribute `at`, e.g.

            init(object(destination,d), value(at,(x,y))).

        states that destination `d` is located at coordinates `(x,y)`


# Output Format<a id="org544aa9b"></a>

All planned actions are represented as `occurs/3` facts of the format

    occurs(object(<object-type>, <object-id>), action(<action-type>, <action-args>), <time step>)

where

-   function `object` refers to an object by its type `<object-type>` and relative identifier `<object-id>`,
    e.g. `object(robot, 34)` for a robot with RID 34
-   function `action` specifies the type of action `<action-type>` together with a tuple of input
    arguments `<action-args>` to be executed by the associated object; specifically, actions
    are so far only defined for object type `robot` with the following action types:
    -   `move`
        - tells the robot to move in a cardinal direction to an adjacent grid node
        - takes a binary `<action-args>` tuple with the domain `(-1,0), (1,0), (0,-1), (0,1)` that
            indicates the four possible movement directions 'West, East, South, North' in relation to
            the robot's current location
    -   `pickup`
        - tells the robot to pick up the shelf at its current location
        - takes an empty `<action-args>` tuple
    -   `putdown`
        - tells the robot to put down the shelf at its current location
        - takes an empty `<action-args>` tuple
    -   `deliver`
        -   for [domain A](#cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b) (i.e. plans that consider product quantities):
            -   tells the robot to deliver a certain amount of units of a product to (partially) fill a specific order
            -   is only applicable if robot is at a picking station
            -   takes as `<action-args>` a triple comprised by
                1. the object ID of the order
                2. the object ID by the Product
                3. the number of product units
        -   in case that [product quantities are ignored](#cid-49448523-5e9b-4ed2-ac1a-6754d838b85c):
            -   tells the robot to deliver a product to fill a specific order
            -   is only applicable if robot is at a picking station
            -   takes as `<action-args>` a tuple comprised by
                1. the object ID of the order
                2. the object ID by the Product
-   `<time step>` is an integer constant equal to the time step when the action should be performed


# Example Instance and Plan<a id="org3cd67c7"></a>

This is an example rooted in [domain A](#cid-b0f981f8-3202-42c0-a46e-aa6f1a52629b). All files related to this example can be
found in `./examples/dom-a/small/`.

## Instance<a id="org10e2bf4"></a>

Visualization of the instance below (robots are depicted as single colored squares, shelves as
circles, picking stations as yellow and black striped squares, and highway nodes as gray fields):

![img](img/example_inst.png "Visualization of instance `./examples/dom-a/small/x11_y6_n66_r3_s12_ps2_pr5_u50_o3_N001.lp`")

Instance file at `./examples/dom-a/small/x11_y6_n66_r3_s12_ps2_pr5_u50_o3_N001.lp`:

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Grid Size X:                      11
    % Grid Size Y:                      6
    % Number of Nodes:                  66
    % Number of Highway Nodes:          45
    % Number of Robots:                 3
    % Number of Shelves:                12
    % Number of Picking Stations:       2
    % Number of Products:               5
    % Number of Product Units in Total: 50
    % Number of Orders:                 3
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    #program base.

    %
    % Warehouse grid nodes
    %
    init(object(node,1),value(at,(1,1))).
    init(object(node,2),value(at,(2,1))).
    init(object(node,3),value(at,(3,1))).
    init(object(node,4),value(at,(4,1))).
    init(object(node,5),value(at,(5,1))).
    init(object(node,6),value(at,(6,1))).
    init(object(node,7),value(at,(7,1))).
    init(object(node,8),value(at,(8,1))).
    init(object(node,9),value(at,(9,1))).
    init(object(node,10),value(at,(10,1))).
    init(object(node,11),value(at,(11,1))).
    init(object(node,12),value(at,(1,2))).
    init(object(node,13),value(at,(2,2))).
    init(object(node,14),value(at,(3,2))).
    init(object(node,15),value(at,(4,2))).
    init(object(node,16),value(at,(5,2))).
    init(object(node,17),value(at,(6,2))).
    init(object(node,18),value(at,(7,2))).
    init(object(node,19),value(at,(8,2))).
    init(object(node,20),value(at,(9,2))).
    init(object(node,21),value(at,(10,2))).
    init(object(node,22),value(at,(11,2))).
    init(object(node,23),value(at,(1,3))).
    init(object(node,24),value(at,(2,3))).
    init(object(node,25),value(at,(3,3))).
    init(object(node,26),value(at,(4,3))).
    init(object(node,27),value(at,(5,3))).
    init(object(node,28),value(at,(6,3))).
    init(object(node,29),value(at,(7,3))).
    init(object(node,30),value(at,(8,3))).
    init(object(node,31),value(at,(9,3))).
    init(object(node,32),value(at,(10,3))).
    init(object(node,33),value(at,(11,3))).
    init(object(node,34),value(at,(1,4))).
    init(object(node,35),value(at,(2,4))).
    init(object(node,36),value(at,(3,4))).
    init(object(node,37),value(at,(4,4))).
    init(object(node,38),value(at,(5,4))).
    init(object(node,39),value(at,(6,4))).
    init(object(node,40),value(at,(7,4))).
    init(object(node,41),value(at,(8,4))).
    init(object(node,42),value(at,(9,4))).
    init(object(node,43),value(at,(10,4))).
    init(object(node,44),value(at,(11,4))).
    init(object(node,45),value(at,(1,5))).
    init(object(node,46),value(at,(2,5))).
    init(object(node,47),value(at,(3,5))).
    init(object(node,48),value(at,(4,5))).
    init(object(node,49),value(at,(5,5))).
    init(object(node,50),value(at,(6,5))).
    init(object(node,51),value(at,(7,5))).
    init(object(node,52),value(at,(8,5))).
    init(object(node,53),value(at,(9,5))).
    init(object(node,54),value(at,(10,5))).
    init(object(node,55),value(at,(11,5))).
    init(object(node,56),value(at,(1,6))).
    init(object(node,57),value(at,(2,6))).
    init(object(node,58),value(at,(3,6))).
    init(object(node,59),value(at,(4,6))).
    init(object(node,60),value(at,(5,6))).
    init(object(node,61),value(at,(6,6))).
    init(object(node,62),value(at,(7,6))).
    init(object(node,63),value(at,(8,6))).
    init(object(node,64),value(at,(9,6))).
    init(object(node,65),value(at,(10,6))).
    init(object(node,66),value(at,(11,6))).

    %
    % Highway grid nodes
    %
    init(object(highway,1),value(at,(1,1))).
    init(object(highway,2),value(at,(2,1))).
    init(object(highway,3),value(at,(3,1))).
    init(object(highway,5),value(at,(5,1))).
    init(object(highway,6),value(at,(6,1))).
    init(object(highway,7),value(at,(7,1))).
    init(object(highway,9),value(at,(9,1))).
    init(object(highway,10),value(at,(10,1))).
    init(object(highway,11),value(at,(11,1))).
    init(object(highway,12),value(at,(1,2))).
    init(object(highway,13),value(at,(2,2))).
    init(object(highway,14),value(at,(3,2))).
    init(object(highway,15),value(at,(4,2))).
    init(object(highway,16),value(at,(5,2))).
    init(object(highway,17),value(at,(6,2))).
    init(object(highway,18),value(at,(7,2))).
    init(object(highway,19),value(at,(8,2))).
    init(object(highway,20),value(at,(9,2))).
    init(object(highway,21),value(at,(10,2))).
    init(object(highway,22),value(at,(11,2))).
    init(object(highway,23),value(at,(1,3))).
    init(object(highway,28),value(at,(6,3))).
    init(object(highway,33),value(at,(11,3))).
    init(object(highway,34),value(at,(1,4))).
    init(object(highway,39),value(at,(6,4))).
    init(object(highway,44),value(at,(11,4))).
    init(object(highway,45),value(at,(1,5))).
    init(object(highway,46),value(at,(2,5))).
    init(object(highway,47),value(at,(3,5))).
    init(object(highway,48),value(at,(4,5))).
    init(object(highway,49),value(at,(5,5))).
    init(object(highway,50),value(at,(6,5))).
    init(object(highway,51),value(at,(7,5))).
    init(object(highway,52),value(at,(8,5))).
    init(object(highway,53),value(at,(9,5))).
    init(object(highway,54),value(at,(10,5))).
    init(object(highway,55),value(at,(11,5))).
    init(object(highway,59),value(at,(4,6))).
    init(object(highway,60),value(at,(5,6))).
    init(object(highway,61),value(at,(6,6))).
    init(object(highway,62),value(at,(7,6))).
    init(object(highway,63),value(at,(8,6))).
    init(object(highway,64),value(at,(9,6))).
    init(object(highway,65),value(at,(10,6))).
    init(object(highway,66),value(at,(11,6))).

    %
    % Shelves
    %
    init(object(shelf,1),value(at,(3,3))).
    init(object(shelf,2),value(at,(5,3))).
    init(object(shelf,3),value(at,(7,3))).
    init(object(shelf,4),value(at,(8,3))).
    init(object(shelf,5),value(at,(10,3))).
    init(object(shelf,6),value(at,(3,4))).
    init(object(shelf,7),value(at,(4,4))).
    init(object(shelf,8),value(at,(5,4))).
    init(object(shelf,9),value(at,(7,4))).
    init(object(shelf,10),value(at,(8,4))).
    init(object(shelf,11),value(at,(9,4))).
    init(object(shelf,12),value(at,(10,4))).

    %
    % Products on Shelves
    %
    init(object(product,1),value(on,(9,4))).
    init(object(product,1),value(on,(12,4))).
    init(object(product,2),value(on,(2,7))).
    init(object(product,2),value(on,(3,4))).
    init(object(product,3),value(on,(1,8))).
    init(object(product,4),value(on,(1,1))).
    init(object(product,4),value(on,(2,1))).
    init(object(product,4),value(on,(3,1))).
    init(object(product,5),value(on,(1,10))).
    init(object(product,5),value(on,(2,10))).

    %
    % Picking Stations
    %
    init(object(pickingStation,1),value(at,(4,1))).
    init(object(pickingStation,2),value(at,(8,1))).

    %
    % Robots
    %
    init(object(robot,1),value(at,(1,6))).
    init(object(robot,2),value(at,(2,6))).
    init(object(robot,3),value(at,(3,6))).

    %
    % Orders
    %
    init(object(order,1),value(line,(2,11))).
    init(object(order,1),value(line,(4,2))).
    init(object(order,1),value(pickingStation,1)).
    init(object(order,2),value(line,(4,1))).
    init(object(order,2),value(line,(5,20))).
    init(object(order,2),value(pickingStation,2)).
    init(object(order,3),value(line,(1,2))).
    init(object(order,3),value(line,(3,1))).
    init(object(order,3),value(pickingStation,2)).


## Possible Plan<a id="org0cd8844"></a>

Visualization of the plan:

<iframe width="560" height="315" src="https://www.youtube.com/embed/ifYKHIvdnjw" frameborder="0" allowfullscreen></iframe>

Plan file at `./examples/dom-a/small/outcome.txt`:

    occurs(object(robot,1),action(move,(1,0)),1).
    occurs(object(robot,2),action(move,(0,-1)),1).
    occurs(object(robot,3),action(move,(0,-1)),1).
    occurs(object(robot,1),action(move,(1,0)),2).
    occurs(object(robot,2),action(move,(0,-1)),2).
    occurs(object(robot,3),action(move,(0,-1)),2).
    occurs(object(robot,1),action(move,(1,0)),3).
    occurs(object(robot,3),action(move,(0,-1)),3).
    occurs(object(robot,1),action(move,(1,0)),4).
    occurs(object(robot,2),action(move,(1,0)),4).
    occurs(object(robot,3),action(pickup,()),4).
    occurs(object(robot,1),action(move,(0,-1)),5).
    occurs(object(robot,3),action(move,(0,-1)),5).
    occurs(object(robot,1),action(move,(0,-1)),6).
    occurs(object(robot,2),action(move,(1,0)),6).
    occurs(object(robot,3),action(move,(0,-1)),6).
    occurs(object(robot,1),action(move,(0,-1)),7).
    occurs(object(robot,2),action(move,(1,0)),7).
    occurs(object(robot,3),action(move,(1,0)),7).
    occurs(object(robot,2),action(move,(1,0)),8).
    occurs(object(robot,1),action(pickup,()),8).
    occurs(object(robot,3),action(deliver,(1,4,1)),8).
    occurs(object(robot,1),action(move,(0,-1)),9).
    occurs(object(robot,2),action(move,(1,0)),9).
    occurs(object(robot,3),action(move,(1,0)),9).
    occurs(object(robot,1),action(move,(-1,0)),10).
    occurs(object(robot,2),action(move,(0,-1)),10).
    occurs(object(robot,3),action(move,(1,0)),10).
    occurs(object(robot,1),action(move,(0,-1)),11).
    occurs(object(robot,2),action(move,(1,0)),11).
    occurs(object(robot,3),action(move,(1,0)),11).
    occurs(object(robot,3),action(move,(1,0)),12).
    occurs(object(robot,2),action(pickup,()),12).
    occurs(object(robot,1),action(deliver,(1,2,7)),12).
    occurs(object(robot,1),action(move,(1,0)),13).
    occurs(object(robot,2),action(move,(1,0)),13).
    occurs(object(robot,3),action(deliver,(3,3,1)),13).
    occurs(object(robot,1),action(move,(1,0)),14).
    occurs(object(robot,2),action(putdown,()),14).
    occurs(object(robot,3),action(deliver,(2,5,10)),14).
    occurs(object(robot,1),action(move,(1,0)),15).
    occurs(object(robot,2),action(move,(-1,0)),15).
    occurs(object(robot,3),action(move,(0,1)),15).
    occurs(object(robot,1),action(move,(1,0)),16).
    occurs(object(robot,2),action(move,(-1,0)),16).
    occurs(object(robot,3),action(move,(0,1)),16).
    occurs(object(robot,3),action(putdown,()),17).
    occurs(object(robot,3),action(move,(0,1)),18).
    occurs(object(robot,2),action(pickup,()),18).
    occurs(object(robot,1),action(deliver,(2,5,1)),18).
    occurs(object(robot,2),action(move,(-1,0)),19).
    occurs(object(robot,3),action(move,(-1,0)),19).
    occurs(object(robot,1),action(deliver,(2,5,4)),19).
    occurs(object(robot,2),action(move,(0,-1)),20).
    occurs(object(robot,3),action(pickup,()),20).
    occurs(object(robot,2),action(move,(0,-1)),21).
    occurs(object(robot,3),action(move,(0,-1)),21).
    occurs(object(robot,2),action(move,(-1,0)),22).
    occurs(object(robot,3),action(move,(0,-1)),22).
    occurs(object(robot,1),action(deliver,(2,4,1)),22).
    occurs(object(robot,2),action(move,(-1,0)),23).
    occurs(object(robot,3),action(move,(0,-1)),23).
    occurs(object(robot,1),action(deliver,(2,5,5)),23).
    occurs(object(robot,1),action(move,(0,1)),24).
    occurs(object(robot,3),action(move,(1,0)),24).
    occurs(object(robot,2),action(deliver,(1,4,1)),24).
    occurs(object(robot,1),action(move,(-1,0)),25).
    occurs(object(robot,3),action(deliver,(3,1,2)),25).
    occurs(object(robot,1),action(move,(0,1)),26).
    occurs(object(robot,3),action(move,(0,1)),26).
    occurs(object(robot,2),action(deliver,(1,2,4)),26).
    occurs(object(robot,1),action(move,(0,1)),27).
    occurs(object(robot,2),action(move,(0,1)),27).
    occurs(object(robot,3),action(move,(-1,0)),27).
    occurs(object(robot,2),action(move,(0,1)),28).
    occurs(object(robot,3),action(move,(0,1)),28).
    occurs(object(robot,1),action(putdown,()),29).
    occurs(object(robot,2),action(putdown,()),29).
    occurs(object(robot,3),action(putdown,()),29).
