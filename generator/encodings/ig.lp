% = INSTANCE GENERATION ENCODING ===================================================================


% - OBJECT GENERATION ------------------------------------------------------------------------------

% * Template Overhang ******************************************************************************
#program template_stub.
% For templates, each init(object(Type, ID), value(_ ,_)) induces an object(Type, ID)
object(Type, ID) :- init(object(Type, ID), value(_, _)).


% * Floor Nodes ************************************************************************************

% ~~ Number and Inits ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program nodes(x, y, n).
sizeX(x).
sizeY(y).
nodes(n).
poss(object(node), value(at, (X, Y))) :- X = 1..x, Y = 1..y.
n { init(object(node, x * (Y-1) + X), value(at, (X, Y))) : poss(object(node), value(at, (X, Y)))} n.
reachableNode(1).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X + 1, Y))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X - 1, Y))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X, Y + 1))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X, Y - 1))).
:- not reachableNode(N), init(object(node, N), value(at, (_, _))).


% * Robots *****************************************************************************************

% ~~ Number ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program robots(min, max).
1 { robotNum(N) : N = min..max } 1.
object(robot, 1..N) : robotNum(N).

% ~~ Init atoms ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program robots_init.
1 { init(object(robot, ID), value(at, (X,Y))) : poss(robot, at(X,Y)) } 1 :- object(robot, ID).


% * Shelves ****************************************************************************************

% ~~ Number ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% via min/max bounds
#program shelves(min, max).
1 { shelfNum(N) : N = min..max } 1.
object(shelf, 1..N) : shelfNum(N).

% or alternatively, via shelf coverage rate of "storage nodes", i.e.,
% nodes that are neither higway/parking/picking-station nodes
#program shelf_coverage(pct).
% # stoarge nodes = ...
storageNodeNum(N-H-S-P) :- N = #count{ ID : init(object(node, ID),_) }, % # nodes -
                           H = #count{ X, Y : highway(X, Y) },          % # highwaynodes -
                           pickingStationNum(S),                        % # picking-stations -
                           robotNum(P).                                 % # robot-parking-nodes

shelfNum(N) :- N = M * pct / 100; storageNodeNum(M). % percentage-based shelf coverage
object(shelf, 1..N) :- shelfNum(N).

% ~~ Init atoms ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program shelves_init.
1 { init(object(shelf, ID), value(at, (X,Y))) : poss(shelf, at(X,Y)) } 1 :- object(shelf, ID).


% * Picking Stations *******************************************************************************

% ~~ Number ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program picking_stations(min, max).
1 {pickingStationNum(N) : N = min..max} 1.
object(pickingStation, 1..N) : pickingStationNum(N).

% ~~ Init atoms ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program picking_stations_init.
1 { init(object(pickingStation, ID), value(at, (X, Y))) : poss(pickingStation, at(X, Y)) } 1 :- object(pickingStation, ID).


% * Products ***************************************************************************************

% ~~ Number  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program products(min, max).
1 { productNum(N) : N = min..max } 1.
object(product, 1..N) : productNum(N).


% * Product Units **********************************************************************************

% ~~ Number and init atoms ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program product_units(min, max, maxps).
%  Arguments:
%    min, max -- minimum and maximum of overall total number of product units
%    maps     -- maximum number of a product's unit per shelf
1 { poss(object(product, PID), value(on, (SID, NUM))) : NUM=1..maxps } 1 :- object(shelf, SID),  object(product, PID).
{ init(object(product, PID), value(on, (SID, NUM))) : poss(object(product, PID), value(on, (SID, NUM))) }.
:- object(product, PID), not init(object(product, PID), value(on, (_, _))).
:- min > #sum{NUM, PID, SID : init(object(product, PID), value(on, (SID, NUM)))}.
:- max < #sum{NUM, PID, SID : init(object(product, PID), value(on, (SID, NUM)))}.


%% * Orders ****************************************************************************************
#program orders(num).
object(order, 1..num).

#program orders_init(minlines, maxlines).
1 { init(object(order, OID), value(pickingStation, PSID)) : object(pickingStation, PSID) } 1 :- object(order, OID).
%1 { init(object(order, OID), value(line, (PID, N))) : init(object(product, PID), value(on, (SID, NUM))), N=1..NUM } <= maxlines :- object(order, OID).
minlines <= { init(object(order, OID), value(line, (PID, NUM))) : object(product, PID), NUM=1..20 } <= maxlines :- object(order, OID).
:- 2 { init(object(order, OID), value(line, (PID, _))) }, object(product, PID), object(order, OID).

% Don't order more products than available
available(PID, C) :- C = #sum{ NUM, SID : init(object(product, PID), value(on, (SID, NUM))) }, object(product, PID).
ordered(PID, C) :- C = #sum{ NUM, OID : init(object(order, OID), value(line, (PID, NUM))) }, object(product, PID).
:- ordered(PID, OC), available(PID, AC), OC > AC.
%% init(available(PID, C), 0) :- available(PID, C).
%% init(ordered(PID, C), 0) :- ordered(PID, C).

%% create order arrival
%% #program order_arrival(maxT).
%% time(1..max).
%% init(object(order, OID)), value(arrivalDate, T)):


% * General Aspects ********************************************************************************
#program base.
% two objects of the same kind can´t be on the same node
:- init(object(TYPE, ID), value(at, (X, Y))), init(object(TYPE, ID2), value(at, (X, Y))), ID != ID2.
% one object cannot be in two locations
:- 2 { init(object(TYPE, ID), value(at, _)) }, object(TYPE, ID).



% - LAYOUT CONSTRAINTS -----------------------------------------------------------------------------


% * Random Layout **********************************************************************************
#program random_layout(g).
% Arguments:
%   g -- the maximum gaps component size
poss(pickingStation, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).
poss(robot, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).
poss(shelf, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).

% ~~ Evenly spread out gaps ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
gap(SX * (Y-1) + X, X, Y) :- not init(object(node, _), value(at, (X, Y))), X=1..SX, Y=1..SY, sizeX(SX), sizeY(SY).
gap_edge(ID1, ID2)  :- gap(ID1, X-1, Y),   gap(ID2, X, Y).
gap_edge(ID1, ID2)  :- gap(ID1, X, Y-1),   gap(ID2, X, Y).
gap_edge(ID1, ID2)  :- gap(ID1, X-1, Y-1), gap(ID2, X, Y).
gap_edge(ID1, ID2)  :- gap(ID1, X-1, Y),   gap(ID2, X, Y-1).
gap_edge(ID1, ID2)  :- gap_edge(ID2, ID1).
gap_reach(ID1, ID2) :- gap_edge(ID1, ID2).
gap_reach(ID1, ID3) :- gap_reach(ID1, ID2), gap_reach(ID2, ID3).
% limit gap size and only allow 1/2 of all gap nodes to form a maximum size component
:- gap(ID, _, _), g < { gap_reach(ID, _) }.
gap_max(ID)         :- g { gap_reach(ID, _) } g, gap(ID, _, _).
:- M = #count { ID : gap_max(ID) }, M > (SX * SY - N) / 2, nodes(N), sizeX(SX), sizeY(SY).

% * Highway Layout *********************************************************************************
#program highway_layout(x, y, beltway). % x/y storage cluster dimension; beltway-width

% ~~ Create Manhattan-like grid of highway nodes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% Max x-,y-coordinates
%% sizeX(X) :- init(object(node, _), value(at, (X, _))), not init(object(node, _), value(at, (X + 1, _))).
%% sizeY(Y) :- init(object(node, _), value(at, (_, Y))), not init(object(node, _), value(at, (_, Y + 1))).

% Beltway around shelf clusters
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), X <= beltway,
                 Y > PT, paddingTop(PT), Y <= SY-PB, paddingBottom(PB), sizeY(SY).
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), X > SX-beltway, sizeX(SX),
                 Y > PT, paddingTop(PT), Y <= SY-PB, paddingBottom(PB), sizeY(SY).
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), Y > P, Y <= beltway+P, paddingTop(P).
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), Y>SY-beltway-P, Y <= SY-P, sizeY(SY), paddingBottom(P).

% Extra rows for placing picking station and robots, resp., at the top and bottom
paddingTop(Y)    :- Y = (PN-1) / X + 1, sizeX(X), pickingStationNum(PN).
paddingBottom(Y) :- Y = (RN-1) / X + 1, sizeX(X), robotNum(RN).

% Draw grid
highway(X, Y) :- beltway(X,Y).
highway(X, Y) :- highway(X, Y-y-1), init(object(node, _), value(at, (X, Y))), not beltway(X,   Y-y), not beltway(X, Y),
                 Y < SY-P, sizeY(SY), paddingBottom(P).
highway(X, Y) :- highway(X-x-1, Y), init(object(node, _), value(at, (X, Y))), not beltway(X-x-2, Y), not beltway(X, Y),
                 Y < SY-P, sizeY(SY), paddingBottom(P).

% No blanks between picking stations at the top
highway(X,Y) :- not poss(pickingStation, at(X, Y)), Y= 1..P, paddingTop(P), init(object(node, _), value(at, (X, Y))).

% No blanks between robots at bottom, blank nodes represent parking locations for robots
highway(X,Y) :- not poss(robot, at(X, Y)), Y=SY-P+1..SY, paddingBottom(P), sizeY(SY), init(object(node, _), value(at, (X, Y))).

% Init highway nodes
init(object(highway, (Y-1) * SX + X), value(at, (X, Y))) :- highway(X, Y), sizeX(SX).

% ~~ All picking station in top row(s), evenly distributed ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{ poss(pickingStation, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))), Y <= (PN-1) / SX + 1, sizeX(SX), pickingStationNum(PN).
:- PN < #count{ X, Y : poss(pickingStation, at(X,Y)) }, pickingStationNum(PN).
dist_pickingStations(X) : X = SX / PN, sizeX(SX), pickingStationNum(PN). % distance between adjacent picking stations
:- poss(pickingStation, at(X, Y)), init(object(node, _), value(at, (X2, Y))), dist_pickingStations(X - X2), not poss(pickingStation, at(X2, Y)),
   not  dist_pickingStations(1).
:- poss(pickingStation, at(X, Y)), poss(pickingStation, at(X2, Y)), X2 > X, X2 < X + DX, dist_pickingStations(DX),
   not dist_pickingStations(1).
:- poss(pickingStation, at(X, Y)), X < DX, dist_pickingStations(DX). % padding left
% Special case when dist_pickingStations(1) (i.e., amount picking stations > sizeX / 2)
:- poss(pickingStation, at(X, Y)), poss(pickingStation, at(X2, Y)), X2 > X, X2 < X + 2, 2 * (PN - X) <= SX - X,
   sizeX(SX), pickingStationNum(PN), dist_pickingStations(1).

% ~~ All robots in left-lower corner, next to each other ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{ poss(robot, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))), Y > Y2 - ((RN - 1) / X2 + 1), sizeY(Y2), sizeX(X2), robotNum(RN).
:- RN < #count{ X, Y : poss(robot, at(X,Y)) }, robotNum(RN).
:- poss(robot, at(X,Y)), X > X2, init(object(node, _), value(at, (X2, Y))), not poss(robot, at(X2,Y)).

% ~~ Shelves restrictions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
%     Shelves must not:
%       1.) be placed on highways,
%       2.) share locations with robots or pickinstations,
%       3.) be in top or bottom most row.
{ poss(shelf, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))).
:- poss(shelf, at(X, Y)), highway(X, Y).
:- poss(shelf, at(X, Y)), poss(robot, at(X, Y)).
:- poss(shelf, at(X, Y)), poss(pickingStation, at(X, Y)).
:- poss(shelf, at(X, _)), sizeX(X).
:- poss(shelf, at(_, Y)), sizeY(Y).
:- poss(shelf, at(1, _; _, 1)).


% * Shelves Reachability ***************************************************************************
#program reachable_layout().
reachable(object(shelf, ID), node(X, Y)) :- reachable(object(shelf, ID), node(X-1, Y)), init(object(node, _), value(at, (X, Y))),
                                           not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X, Y)) :- reachable(object(shelf, ID), node(X+1, Y)), init(object(node, _), value(at, (X, Y))),
                                           not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X, Y)) :- reachable(object(shelf, ID), node(X, Y-1)), init(object(node, _), value(at, (X, Y))),
                                           not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X,  Y)) :- reachable(object(shelf, ID), node(X, Y+1)), init(object(node, _), value(at, (X, Y))),
                                           not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X, Y)) :- init(object(shelf, ID), value(at, (X, Y))).

:- init(object(pickingStation, StationID), value(at, (X,Y))), not reachable(object(shelf, ShelfID), node(X, Y)), object(shelf, ShelfID).



% - ORDER CONSTRAINTS AND OPTIMIZATIONS ------------------------------------------------------------


% * All Products Have To Be Ordered At Least Once **************************************************
#program order_all_products.
:- object(product, PID), not init(object(order, _), value(line, (PID, _))).


% * Assign Orders To Pickingstations Evenly ********************************************************
#program order_to_ps_evenly.
#maximize{ PSID : init(object(order,_), value(pickingStation, PSID)) }.


% * Orders Contain As Many Different Products As Possible ******************************************
#program orders_different.
#minimize{ PID, OID, OID2 : init(object(order, OID), value(line, (PID, _))),
                            init(object(order, OID2), value(line, (PID, _))) }.



% - PROJECTION TO SPECIFIC INIT ATOMS --------------------------------------------------------------


% * All inits **************************************************************************************
#program project_all.
#show.
#show init(O, V): init(O, V).


% * Only Orders ************************************************************************************
#program project_orders.
#show.
#show init(object(order, ID), V) : init(object(order, ID), V).


% * All Warehouse Objects Except Orders ************************************************************
#program project_warehouse.
#show.
#show init(object(O, ID) ,V) : init(object(O, ID), V), not O == order.
