% = FILTER ENCODINGS FOR INCREMENTAL GENERATION ====================================================


#program picking_stations().
%  Arguments:
%    max_top_row -- Maximum y-coordinate reserved for picking stations
highway_layout :- init(object(highway, _), _).
max_top_row(YY-1) :- YY = #min{ Y : init(object(highway, ID), value(at, (_, Y))) }, YY > 0, highway_layout.
select(object(node, ID), value(at, (X, Y))) :- init(object(node, ID), value(at, (X, Y))), Y <= MY, max_top_row(MY), highway_layout.
select(object(node, ID), value(at, (X, Y))) :- init(object(node, ID), value(at, (X, Y))), not init(object(pickingStation, _), value(at, (X, Y))), not highway_layout.

#program robots().
%  Arguments:
%    min_bottom_row -- Minimum y-coordinate reserved for robots
highway_layout :- init(object(highway, _), _).
min_bottom_row(YY+1) :- YY = #max{ Y : init(object(highway, ID), value(at, (_, Y))) }, YY > 0, highway_layout.
select(object(node, ID), value(at, (X, Y))) :- init(object(node, ID), value(at, (X, Y))), Y >= MY, min_bottom_row(MY), highway_layout.
select(object(node, ID), value(at, (X, Y))) :- init(object(node, ID), value(at, (X, Y))), not init(object(robot, _), value(at, (X, Y))), not highway_layout.

#program shelves.
% Filter nodes occupied by another shelf ...
blocking_otype(shelf).
% .. and in case of highway layout (here detected by existence of highway nodes),
% filter highway nodes, nodes w/ picking station, nodes w/ robots
blocking_otype(highway; pickingStation; robot) :- init(object(highway, _), _).
occupied(ID) :- init(object(node, ID), value(at, XY)), init(object(O, _), value(at, XY)), blocking_otype(O).
select(object(node, ID), V) :- init(object(node, ID), V), not occupied(ID).

#program products.
% Select all shelves
select(object(shelf, ID), V) :- init(object(shelf, ID), V).

#program orders.
% Select all product and picking station facts
select(object(product, ID), V) :- init(object(product, ID), V).
select(object(pickingStation, ID), V) :- init(object(pickingStation, ID), V).

%% % * Output only selected facts *********************************************************************

#program project.
#show.
%#show init(O, V) : select(O, V).
#show init(O, V) : select(O, V).
