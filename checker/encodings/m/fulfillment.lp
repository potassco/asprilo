% = ORDER FULFILLMENT ==============================================================================
%
%   Sequence of actions and conditions required to fulfill (i.e., fully process) an order.
%

% Auxilliary fluents to indicate permanent parking of robots.
holds(object(robot, R), value(moves,       ()), T)   :- occurs(object(robot, R), action(move, _), T).
holds(object(robot, R), value(perma_parks, ()), H)   :- init(object(robot, R), _), horizon(H).
holds(object(robot, R), value(perma_parks, ()), T-1) :- not holds(object(robot, R), value(moves, ()), T);
                                                            holds(object(robot, R), value(perma_parks, ()), T);
                                                            init( object(robot, R), _                        );
                                                            time(T; T-1).

% Remove outdated order lines, i.e., order is fulfilled as soon as robot permanently parks under
% shelf for the remainder of the plan
ab(object(order, O), value(line, (P, RQ)), T) :- holds(object(robot,   R),  value(at,          (X, Y)),  T  );
                                                 holds(object(robot,   R),  value(perma_parks, ()),      T  );
                                                 holds(object(shelf,   S),  value(at,          (X, Y)),  T  );
                                                 holds(object(order,   O),  value(line,        (P, RQ)), T-1);
                                                 holds(object(product, P),  value(on,          (S,  _)), T-1).

