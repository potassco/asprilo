% = PROBLEM INSTANCE REPRESENTATION ================================================

% - Objects -------------------------------------------------------------------

node(X,Y)    :- init(object(node, _),           value(at, (X, Y))).
highway(X,Y) :- init(object(highway, _),        value(at, (X, Y))).
robot(R)     :- init(object(robot, R),                          _).
shelf(S)     :- init(object(shelf, S),                          _).
station(P)   :- init(object(pickingStation, P),                 _).
product(A)   :- init(object(product, A),                        _).
order(O)     :- init(object(order, O),                          _).

% - Static Relations -----------------------------------------------------------

assigned(O, P)                         :- init(object(order, O),  value(pickingStation, P)).
at(station(P), X, Y, 0)                :- init(object(station, P), value(at, (X, Y))).

% - Fluents ---------------------------------------------------------------------

at(robot(R), X, Y, 0)                  :- init(object(robot, R), value(at, (X, Y))).
at(shelf(S), X, Y, 0)                  :- init(object(shelf, S), value(at, (X, Y))).
on(A, S, Q, 0)                         :- init(object(product, A), value(on, (S, Q))). % products on shelfs
open(O, A, Q, 0)                       :- init(object(order, O), value(line, (A, Q))). % unfullfilled order line
