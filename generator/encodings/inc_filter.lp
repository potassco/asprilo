% = FILTER ENCODINGS FOR INCREMENTAL GENERATION ====================================================


#program picking_stations().
%  Arguments:
%    max_top_row -- Maximum y-coordinate reserved for picking stations
highway_layout :- init(object(highway, _), _).
max_top_row(YY-1) :- YY = #min{ Y : init(object(highway, ID), value(at, (_, Y))) }, YY > 0.
select(object(node, ID), value(at, (X, Y))) :- init(object(node, ID), value(at, (X, Y))), Y <= MY, max_top_row(MY).

#program robots().
%  Arguments:
%    min_bottom_row -- Minimum y-coordinate reserved for robots
min_bottom_row(YY+1) :- YY = #max{ Y : init(object(highway, ID), value(at, (_, Y))) }, YY > 0.
select(object(node, ID), value(at, (X, Y))) :- init(object(node, ID), value(at, (X, Y))), Y >= MY, min_bottom_row(MY).

%% #program shelves(padding_bot, padding_top).
#program shelves.
% Filter nodes occupied by another shelf ...
blocking_otype(shelf).
% .. and in case of highway layout (here detected by existence of highway nodes),
% filter highway nodes, nodes w/ picking station, nodes w/ robots
blocking_otype(highway; pickingStation; robot) :- init(object(highway, _), _).
occupied(ID) :- init(object(node, ID), value(at, XY)), init(object(O, _), value(at, XY)), blocking_otype(O).
select(object(node, ID), V) :- init(object(node, ID), V), not occupied(ID).



%select(node, ID) :- init(object(node, ID), _).
%select(O, V) :- init(O, V).
%% % * Output only selected facts *********************************************************************

#program project.
#show.
%#show init(O, V) : select(O, V).
#show init(O, V) : select(O, V).
