% = INSTANCE GENERATION ENCODING ===================================================================


% - OBJECT GENERATION ------------------------------------------------------------------------------



% * Template Overhang ******************************************************************************

#program template_stub.
% For templates, each init(object(Type, ID), value(_ ,_)) induces an object(Type, ID)
%object(Type, ID) :- init(object(Type, ID), _).
template.
object(Type, ID) :- init(object(Type, ID), _).
template(object(Type, ID)) :- init(object(Type, ID), _).
template(init(object(Type, ID), value(Attr, Value))) :- init(object(Type, ID), value(Attr, Value)).


% * Floor Nodes ************************************************************************************

% ~~ Number, IDs and Init Facts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% Initiale program nodes based on quantities given via command line
#program nodes(x, y, n).
poss(object(node), value(at, (X, Y))) :- X = 1..x, Y = 1..y.
n { init(object(node, x * (Y-1) + X), value(at, (X, Y))) : poss(object(node), value(at, (X, Y)))} n.
% All nodes must be in one component (pairwise reachable)
reachableNode(1).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X + 1, Y))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X - 1, Y))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X, Y + 1))).
reachableNode(N2) :- reachableNode(N), init(object(node, N), value(at, (X, Y))), init(object(node, N2), value(at, (X, Y - 1))).
:- not reachableNode(N), init(object(node, N), value(at, (_, _))).


% Determine dimensions, i.e., maximum x-,y-coordinates and the total number of nodes
% - This variant also supprt
#program floor_dimensions.
sizeX(MX) :- MX = #max{    X : init(object(node, _),  value(at, (X, _))); 1 }, MX > 0.
sizeY(MY) :- MY = #max{    Y : init(object(node, _),  value(at, (_, Y))); 1 }, MY > 0.
nodes(N)  :- N  = #count{ ID : init(object(node, ID), value(at, (_, _))) }, N > 0.


% * Robots *****************************************************************************************

% ~~ Number and IDs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% Amount via min/max bounds from command line options
#program robots_cl(min, max).
1 { robot_amount_choice(N) : N = min..max } 1.
% Robot ID domain.
robot_id_dom(1..N) :- robot_amount_choice(N).


% Quantity and IDs based on command line parameters and an optional template
#program robots.
% Robot ID domain including IDs from template facts if present
robot_id_dom(ID) :- object(robot, ID).

% Initialize robots based on the maximum of the quantities given as command line arg and template
% facts
robot_amount(N) :- N = #max{ ID : object(robot, ID); M : robot_amount_choice(M) }, robot_id_dom(N).
object(robot, 1..N) :- robot_amount(N).

%% % Template stub for robots if their quantity is exclusively specified via a template but not via
%% % command line options
%% #program robots_template_only.
%% robot_amount(N) :- #count{ ID: object(robot, ID)}


% ~~ Init Facts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#program robots_init.
1 { init(object(robot, ID), value(at, (X,Y))) : poss(robot, at(X,Y)) } 1 :-              object(robot, ID),
                                                                            not template(object(robot, ID)).



% * Shelves *****************************************************************************************

% ~~ Number and IDs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% Amount via min/max bounds from command line options
#program shelves_cl(min, max).
1 { shelf_amount_choice(N) : N = min..max } 1.
% Shelf ID domain
shelf_id_dom(1..N) :- shelf_amount_choice(N).


% Quantity and IDs based on command line parameters and an optional template
#program shelves.
% Shelf ID domain including IDs from template facts if present
shelf_id_dom(ID) :- object(shelf, ID).

% Initialize shelfs based on the maximum of the quantities given as command line arg and template
% facts
shelf_amount(N) :- N = #max{ ID : object(shelf, ID); M : shelf_amount_choice(M) }, shelf_id_dom(N).
object(shelf, 1..N) :- shelf_amount(N).


% ... or alternatively, via shelf coverage rate of "storage nodes", i.e.,
% nodes that are neither higway/parking/picking-station nodes
#program shelf_coverage(pct).

% # storage nodes = ...
storageNode_amount(N-H-S-P) :- nodes(N),                                   % # nodes -
                               H = #count{ X, Y : highway(X, Y) },         % # highwaynodes -
                               S = #max{ M : pickingStation_amount(M); 0}, % # picking-stations -
                               P = #max{ M : robot_amount(M); 0},          % # robot-parking-nodes
                               H >= 0, S >= 0, P >= 0.

shelf_amount(N) :- N = (M * pct / 100) + 1, storageNode_amount(M). % percentage-based shelf coverage
object(shelf, 1..N) :- shelf_amount(N).

% ~~ Init Facts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#program shelves_init.
1 { init(object(shelf, ID), value(at, (X,Y))) : poss(shelf, at(X,Y)) } 1 :-              object(shelf, ID),
                                                                            not template(object(shelf, ID)).



% * Picking Stations *******************************************************************************

% ~~ Number and IDs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% Amount via min/max bounds from command line options
#program picking_stations_cl(min, max).
1 {pickingStation_amount_choice(N) : N = min..max} 1.
% Picking station ID domain
pickingStation_id_dom(1..N) :- pickingStation_amount_choice(N).

% Initialize picking stations based on the maximum of the quantities given as command line arg and
% template facts
#program picking_stations.
% Picking station ID domain including IDs from template facts if present
pickingStation_id_dom(ID) :- object(pickingStation, ID).

% Initialize picking stations based on the maximum of the quantities given  as command line arg and template facts
pickingStation_amount(N) :- N = #max{ ID : object(pickingStation, ID); M : pickingStation_amount_choice(M) }, pickingStation_id_dom(N).
object(pickingStation, 1..N) :- pickingStation_amount(N).

% ~~ Init Facts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#program picking_stations_init.
1 { init(object(pickingStation, ID), value(at, (X, Y))) : poss(pickingStation, at(X, Y)) } 1 :-              object(pickingStation, ID),
                                                                                                not template(object(pickingStation, ID)).



% * Products ***************************************************************************************

% ~~ Number and IDs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program products_cl(min, max).

% Amount via min/max bounds from command line options
1 { product_amount_choice(N) : N = min..max } 1.
% Product ID domain
product_id_dom(1..max).

% Initialize products based on the maximum of the quantities given as command line arg and template
% facts
#program products.
% Product ID domain including IDs from template facts if present
product_id_dom(ID) :- object(product, ID).

% Initialize products based on the maximum of the quantities given  as command line arg and template facts
product_amount(N) :- N = #max{ ID : object(product, ID); M : product_amount_choice(M) }, product_id_dom(N).
object(product, 1..N) :- product_amount(N).


% * Product Units **********************************************************************************

% ~~ Number and init atoms ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#program product_units(min, max, minpus, maxpus, minprs, maxprs, minspr, maxspr, cnd_minprs).
%  Arguments:
%    min        -- minimum of overall total number of product units
%    max        -- maximum of overall total number of product units
%    minpus     -- minimum number of a product's units per shelf
%    maxpus     -- maximum number of a product's units per shelf
%    minprs     -- minimum number of products per shelf
%    maxprs     -- maximum number of products per shelf
%    minspr     -- minimum number of shelfs that contain the same product
%    maxspr     -- maximum number of shelfs that contain the same product
%    cnd_minprs -- flags conditional usage of minprs constraint, required for incremental mode
minpus(minpus).
maxpus(maxpus).
{ product_on(PID, SID) } 1 :- object(shelf, SID), object(product, PID), not template(init(object(product, PID), _)).
{ init(object(product, PID), value(on, (SID, NUM))): NUM=M..N, minpus(M), maxpus(N) } = 1 :- product_on(PID, SID).

:- object(product, PID), not init(object(product, PID), value(on, _)).
:- min > #sum{NUM, PID, SID : init(object(product, PID), value(on, (SID, NUM)))}.
:- max < #sum{NUM, PID, SID : init(object(product, PID), value(on, (SID, NUM)))}.

activate_minprs :- minprs < { init(object(product, PID), value(on, (SID, NUM))) }, object(shelf,   SID), cnd_minprs = 1.
activate_minprs :- cnd_minprs = 0.
:- minprs > { init(object(product, PID), value(on, (SID, NUM))) }, object(shelf,   SID), activate_minprs.
:- maxprs < { init(object(product, PID), value(on, (SID, NUM))) }, object(shelf,   SID).
:- minspr > { init(object(product, PID), value(on, (SID, NUM))) }, object(product, PID).
:- maxspr < { init(object(product, PID), value(on, (SID, NUM))) }, object(product, PID).

% Regarding template input: no explicit rules required!


%% * Orders ****************************************************************************************

#program orders(num).
object(order, 1..num).

#program orders_init(minlines, maxlines, maxpupr).
% Arguments:
%   {min|max}lines -- minimum and maximum order lines per order
%   maxpupr        -- maximum units per product

1 { init(object(order, OID), value(pickingStation, PSID)) : object(pickingStation, PSID) } 1 :- object(order, OID),
                                                                                                not template(object(order, OID)).
%1 { init(object(order, OID), value(line, (PID, N))) : init(object(product, PID), value(on, (SID, NUM))), N=1..NUM } <= maxlines :- object(order, OID).
minlines <= { init(object(order, OID), value(line, (PID, NUM))) : object(product, PID), NUM=1..20 } <= maxlines :-              object(order, OID),
                                                                                                                   not template(object(order, OID)).
:- 2 { init(object(order, OID), value(line, (PID, _))) }, object(product, PID), object(order, OID).

% Don't order more products than available
:- #sum{ NUM, SID : init(object(product, PID), value(on, (SID, NUM))) } > maxpupr, object(product, PID).
:- #sum{ NUM, SID : init(object(product, PID), value(on, (SID, NUM))) } < 0,       object(product, PID).
:- #sum{ NUM, OID : init(object(order, OID), value(line, (PID, NUM))) } > maxpupr, object(product, PID).
:- #sum{ NUM, OID : init(object(order, OID), value(line, (PID, NUM))) } < 0,       object(product, PID).
:- AC = #sum{ NUM, SID : init(object(product, PID), value(on, (SID, NUM))) },
   OC = #sum{ NUM, OID : init(object(order, OID), value(line, (PID, NUM))) },
   object(product, PID), OC > AC, AC > 0, OC > 0, AC <= maxpupr, OC <= maxpupr.

% Regarding template input: no explicit rules required!



% * General Aspects ********************************************************************************

#program base.
% two objects of the same kind can´t be on the same node
:- init(object(TYPE, ID), value(at, (X, Y))), init(object(TYPE, ID2), value(at, (X, Y))), ID < ID2.
% one object cannot be in two locations
:- 2 { init(object(TYPE, ID), value(at, _)) }, object(TYPE, ID).

#program symmetry.
% Lexicographical symmetry breaking
sym_object(robot; shelf; pickingStation).
sym_assign(TYPE, ID, V) :- sym_object(TYPE), init(object(TYPE, ID), value(at, (X, Y))), V = (Y-1) * SX + X, sizeX(SX), not template.
sym_enabled(TYPE, ID, V) :- sym_assign(TYPE, ID, V), ID <= V, 1 < ID.
sym_enabled(TYPE, ID, V-1) :- sym_enabled(TYPE, ID, V), ID <= V.
:- sym_assign(TYPE, ID, V), sym_object(TYPE), not sym_enabled(TYPE, ID+1, V), object(TYPE, ID+1), not template.


% - LAYOUT CONSTRAINTS -----------------------------------------------------------------------------


% * Random Layout **********************************************************************************

#program random_layout.
% Arguments:
%   g -- the maximum gaps component size
poss(pickingStation, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).
poss(robot, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).
poss(shelf, at(X, Y)) :- init(object(node, _), value(at, (X, Y))).

% ~~ Evenly spread out gaps ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#program grid_gaps(g).
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

#program highway_layout(x, y, beltway, ph_pickstas, ph_robots).
%  Arguments:
%    x/y           -- storage cluster dimension
%    beltway       -- beltway-width
%    ph_robots     -- placeholder for amount of robots: i.e., the amount of robots to be added in the future
%    ph_pickstas   -- placeholder for amount of picking stations: i.e., the amount of robots to be added in the future

% ~~ Create Manhattan-like grid of highway nodes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

% Beltway around shelf clusters
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), X <= beltway,
                 Y > PT, paddingTop(PT), Y <= SY-PB, paddingBottom(PB), sizeY(SY).
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), X > SX-beltway, sizeX(SX),
                 Y > PT, paddingTop(PT), Y <= SY-PB, paddingBottom(PB), sizeY(SY).
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), Y > P, Y <= beltway+P, paddingTop(P).
beltway(X,Y) :-  init(object(node, _), value(at, (X, Y))), Y>SY-beltway-P, Y <= SY-P, sizeY(SY), paddingBottom(P).

% Extra rows for placing picking station and robots, resp., at the top and bottom
ph_robots(ph_robots).
ph_pickstas(ph_pickstas).
robot_amount_rel(RN)          :- RN = #max{ M : robot_amount(M); N : ph_robots(N); 1 }, RN > 0.
pickingStation_amount_rel(PN) :- PN = #max{ M : pickingStation_amount(M); N : ph_pickstas(N); 1 }, PN > 0.
paddingTop(Y)                 :- Y = (PN-1) / X + 1, sizeX(X), pickingStation_amount_rel(PN).
paddingBottom(Y)              :- Y = (RN-1) / X + 1, sizeX(X), robot_amount_rel(RN).

% Draw highway
highway(X, Y) :- beltway(X,Y).
highway(X, Y) :- highway(X, Y-y-1), init(object(node, _), value(at, (X, Y))), not beltway(X,   Y-y), not beltway(X, Y),
                 Y > PT, Y < SY-PB, sizeY(SY), paddingTop(PT), paddingBottom(PB).
highway(X, Y) :- highway(X-x-1, Y), init(object(node, _), value(at, (X, Y))), not beltway(X-x-2, Y), not beltway(X, Y),
                 Y > PT, Y < SY-PB, sizeY(SY), paddingTop(PT), paddingBottom(PB).

% ... withn no blanks between picking stations at the top
highway(X,Y) :- not poss(pickingStation, at(X, Y)), Y= 1..P, paddingTop(P), init(object(node, _), value(at, (X, Y))),
                pickingStation_amount(_).

% ,,, with no blanks between robots at bottom, blank nodes represent parking locations for robots
highway(X,Y) :- not poss(robot, at(X, Y)), Y=SY-P+1..SY, paddingBottom(P), sizeY(SY), init(object(node, _), value(at, (X, Y))),
                robot_amount(_).

% Init highway nodes
init(object(highway, (Y-1) * SX + X), value(at, (X, Y))) :- highway(X, Y), sizeX(SX).

% ~~ All picking station in top row(s), evenly distributed ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{ poss(pickingStation, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))), Y <= (PN-1) / SX + 1,
                                        sizeX(SX), pickingStation_amount(PN).
poss(pickingStation, at(X, Y))       :- template(init(object(pickingStation, _), value(at, (X,Y)))).

:- PN < #count{ X, Y : poss(pickingStation, at(X,Y)) }, pickingStation_amount(PN).
:- PN > #count{ X, Y : poss(pickingStation, at(X,Y)) }, pickingStation_amount(PN).

dist_pickingStations(X) :- X = (SX+2) / (PN+1), sizeX(SX), pickingStation_amount(PN). % distance between adjacent picking stations
:- poss(pickingStation, at(X, Y)), init(object(node, _), value(at, (X2, Y))), dist_pickingStations(X - X2),
   not poss(pickingStation, at(X2, Y)), not dist_pickingStations(1). % place next pickingstation after DX-1 free slots
:- poss(pickingStation, at(X, Y)), poss(pickingStation, at(X2, Y)), X2 > X, X2 < X + DX, dist_pickingStations(DX),
   not dist_pickingStations(1). % but do not place picking station inside the DX-1 long gaps
:- poss(pickingStation, at(X, Y)), X < DX, dist_pickingStations(DX). % padding left
% Special case when dist_pickingStations(1) (i.e., amount picking stations > sizeX / 2)
:- poss(pickingStation, at(X, Y)), poss(pickingStation, at(X2, Y)), X2 > X, X2 < X + 2, 2 * (PN - X) <= SX - X,
   sizeX(SX), pickingStation_amount(PN), dist_pickingStations(1).

% ~~ All robots in left-lower corner, next to each other ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
xcoord(1..SX)                :- sizeX(SX).
poss(robot, at(1,   SY ), 1) :- sizeY(SY), robot_amount(_).
poss(robot, at(X+1, Y  ), N) :- poss(robot, at(X,  Y), N-1), xcoord(X+1), robot_id_dom(N).
poss(robot, at(1,   Y-1), N) :- poss(robot, at(SX, Y), N-1), sizeX(SX  ), robot_id_dom(N).

poss(robot, at(X,    Y))     :- poss(robot, at(X,  Y),   _).
poss(robot, at(X,    Y))     :- template(init(object(robot, _), value(at, (X, Y)))).

% ~~ Shelves placement and restrictions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{ poss(shelf, at(X, Y)) } 1 :- init(object(node, _), value(at, (X, Y))), shelf_amount(_).
poss(shelf, at(X,Y))        :- template(init(object(shelf, _), value(at, (X, Y)))).
% Shelves must not be placed ...
:- poss(shelf, at(X, Y)), highway(X, Y).                  % on highways;
:- poss(shelf, at(X, Y)), poss(robot, at(X, Y)).          % on robot locations;
:- poss(shelf, at(X, Y)), poss(pickingStation, at(X, Y)). % on picking station locations;
:- poss(shelf, at(X, _)), sizeX(X).                       % in the top row;
:- poss(shelf, at(_, Y)), sizeY(Y).                       % in the bottom row;
:- poss(shelf, at(1, _; _, 1)).                           % on the left and right edge.


% * Shelves Reachability ***************************************************************************

%     All shelves have to be reachable from each pickingstation w/o moving other shelves
#program reachable_shelves().
reachable(object(shelf, ID), node(X, Y))  :- reachable(object(shelf, ID), node(X-1, Y)), init(object(node, _), value(at, (X, Y))),
                                             not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X, Y))  :- reachable(object(shelf, ID), node(X+1, Y)), init(object(node, _), value(at, (X, Y))),
                                             not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X, Y))  :- reachable(object(shelf, ID), node(X, Y-1)), init(object(node, _), value(at, (X, Y))),
                                             not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X,  Y)) :- reachable(object(shelf, ID), node(X, Y+1)), init(object(node, _), value(at, (X, Y))),
                                             not init(object(shelf, _), value(at, (X, Y))).
reachable(object(shelf, ID), node(X, Y)) :-  init(object(shelf, ID), value(at, (X, Y))).

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
