%% template overhang
#program template_stub.
%%% for templates: each init(object(Type, ID), value(_)) induces an object(Type, ID)
object(Type, ID) :- init(object(Type, ID), value(_,_)).


%% create nodes
#program nodes(x, y, n).
poss(object(node), value(at, (X, Y))) :- X = 1..x, Y = 1..y.
n { init(object(node, x * (Y-1) + X), value(at, (X, Y))) : poss(object(node), value(at, (X, Y)))} n.
reachableNode(1).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X + 1, Y))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X - 1, Y))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X, Y + 1))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X, Y - 1))).
:- not reachableNode(N), init(object(node, N), value(at, (_, _))).

%% create robots
#program robots(min, max).
1 { robotNum(N) : N = min..max } 1.
object(robot, 1..N) : robotNum(N).

#program robots_init.
1 { init(object(robot, ID), value(at, (X,Y))) : poss(robot, at(X,Y)) } 1 :- object(robot, ID).

%% create shelves
#program shelves(min, max).
1 { shelfNum(N) : N = min..max } 1.
object(shelf, 1..N) : shelfNum(N).

#program shelves_init.
1 { init(object(shelf, ID), value(at, (X,Y))) : poss(shelf, at(X,Y)) } 1 :- object(shelf, ID).

%% create picking stations
#program picking_stations(min, max).
1 {pickingStationNum(N) : N = min..max} 1.
object(pickingStation, 1..N) : pickingStationNum(N).

#program picking_stations_init.
1 { init(object(pickingStation, ID), value(at, (X, Y))) : poss(pickingStation, at(X, Y)) } 1 :- object(pickingStation, ID).

%% create products
#program products(min, max).
1 { productNum(N) : N = min..max } 1.
object(product, 1..N) : productNum(N).

%% create product units
#program product_units(min, max, maxps). % min and max of overall total number of product units, and max number of a product's unit per shelf
1 { poss(object(product, PID), value(on, (SID, NUM))) : NUM=1..maxps } 1 :- object(shelf, SID),  object(product, PID).
{ init(object(product, PID), value(on, (SID, NUM))) : poss(object(product, PID), value(on, (SID, NUM))) }.
:- object(product, PID), not init(object(product, PID), value(on, (_, _))).
:- min > #sum{NUM, PID, SID : init(object(product, PID), value(on, (SID, NUM)))}.
:- max < #sum{NUM, PID, SID : init(object(product, PID), value(on, (SID, NUM)))}.

%% create orders
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

%% general aspects
#program base.
%%% two objects of the same kind can´t be on the same node
:- init(object(TYPE, ID), value(at, (X, Y))), init(object(TYPE, ID2), value(at, (X, Y))), ID != ID2.
%%% one object cannot be in two locations
:- 2 { init(object(TYPE, ID), value(at, _)) }, object(TYPE, ID).


%------------------------------------------------------------

%% layout constraints

%%%%% random layout
#program random_layout().
poss(pickingStation, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).
poss(robot, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).
poss(shelf, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).

%%%%% beltway layout
#program beltway_layout(x, y).
sizeX(X) :- init(object(node, _), value(at, (X, _))), not init(object(node, _), value(at, (X + 1, _))).
sizeY(Y) :- init(object(node, _), value(at, (_, Y))), not init(object(node, _), value(at, (_, Y + 1))).
highway(1, Y) :- init(object(node, _), value(at, (1, Y))).
highway(X, Y) :- init(object(node, _), value(at, (X, Y))), sizeX(X).

highway(X,Y) :- init(object(node, _), value(at, (X, Y))), Y == (PN-1) / X2 + 2, sizeX(X2), pickingStationNum(PN).
highway(X,Y) :- init(object(node, _), value(at, (X, Y))), Y == Y2 - ((RN-1) / X2 + 1), sizeY(Y2), sizeX(X2), robotNum(RN).

highway(X, Y) :- highway(X, Y-y-1), init(object(node, _), value(at, (X, Y))).
highway(X, Y) :- highway(X-x-1, Y), init(object(node, _), value(at, (X, Y))).
init(object(highway, (Y-1) * SX + X), value(at, (X, Y))) :- highway(X, Y), sizeX(SX).

%%%%%%% all picking station in top row(s), evenly distributed
{ poss(pickingStation, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))), Y <= (PN-1) / SX + 1, sizeX(SX), pickingStationNum(PN).
:- PN < #count{ X, Y : poss(pickingStation, at(X,Y)) }, pickingStationNum(PN).
dist_pickingStations(X) : X = SX / PN, sizeX(SX), pickingStationNum(PN). % distance between adjacent picking stations
:- poss(pickingStation, at(X, Y)), init(object(node, _), value(at, (X2, Y))), dist_pickingStations(X - X2), not poss(pickingStation, at(X2, Y)),
   not  dist_pickingStations(1).
:- poss(pickingStation, at(X, Y)), poss(pickingStation, at(X2, Y)), X2 > X, X2 < X + DX, dist_pickingStations(DX),
   not dist_pickingStations(1).
:- poss(pickingStation, at(X, Y)), X < DX, dist_pickingStations(DX). % padding left
% special case when dist_pickingStations(1) (i.e., amount picking stations > sizeX / 2)
:- poss(pickingStation, at(X, Y)), poss(pickingStation, at(X2, Y)), X2 > X, X2 < X + 2, 2 * (PN - X) <= SX - X,
   sizeX(SX), pickingStationNum(PN), dist_pickingStations(1).


%%%%%%% all robots in left-lower corner, next to each other
{ poss(robot, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))), Y > Y2 - ((RN - 1) / X2 + 1), sizeY(Y2), sizeX(X2), robotNum(RN).
:- RN < #count{ X, Y : poss(robot, at(X,Y)) }, robotNum(RN).
:- poss(robot, at(X,Y)), X > X2, init(object(node, _), value(at, (X2, Y))), not poss(robot, at(X2,Y)).

%%%%%% shelves must not: 1.) be placed on highways, 2.) share locations with robots or pickinstations, 3.) be in top or bottom most row
{ poss(shelf, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))).
:- poss(shelf, at(X, Y)), highway(X, Y).
:- poss(shelf, at(X, Y)), poss(robot, at(X, Y)).
:- poss(shelf, at(X, Y)), poss(pickingStation, at(X, Y)).
:- poss(shelf, at(X, _)), sizeX(X).
:- poss(shelf, at(_, Y)), sizeY(Y).
:- poss(shelf, at(1, _; _, 1)).


%%%% shelves reachability
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

%------------------------------------------------------------

%% order constraints and optimizations

%%% All products have to be ordered at least once
#program order_all_products.
:- object(product, PID), not init(object(order, _), value(line, (PID, _))).

%%% assign orders to pickingstations evenly
#program order_to_ps_evenly.
#maximize{ PSID : init(object(order,_), value(pickingStation, PSID)) }.

%%% orders contain as many different products as possible
#program orders_different.
#minimize{ PID, OID, OID2 : init(object(order, OID), value(line, (PID, _))),
			    init(object(order, OID2), value(line, (PID, _))) }.



%%% Projection to spefici init atoms

#program project_all. % all inits
#show.
#show init(O, V): init(O, V).

#program project_orders. % only orders
#show.
#show init(object(order, ID), V) : init(object(order, ID), V).

#program project_warehouse. % all warehouse objects except orders
#show.
#show init(object(O, ID) ,V) : init(object(O, ID), V), not O == order.
