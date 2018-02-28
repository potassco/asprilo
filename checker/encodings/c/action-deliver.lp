% = ACTION: DELIVER ================================================================================

% Action deliver is only implicit!

% - Domain ---------------------------------------------------------------------

action(deliver, (O, P, Q)) :- init(object(order, O), value(line, (P, RQ))),
                              Q = 1..RQ . % RQ and Q are the requested
                                          % and delivered quantity, resp.

% - Preconditions - Verification -----------------------------------------------

% Robot not at picking station
err(deliver, notAtPS, (R, T)) :-     occurs(object(robot,          R), action(deliver, (_, _, _)), T  );
                                     holds(object( robot,          R), value( at,      (X, Y)   ), T-1);
                                 not holds(object( pickingStation, _), value( at,      (X, Y)   ), T-1).

% Robot not carrying a shelf
err(deliver, noShelf, (R, T))  :-     occurs(object(robot, R), action(deliver, (_, _, _)), T);
                                     { holds( object(robot, R), value( carries, S ), T-1) :
                                       holds( object(shelf, S), _                  , T-1) } < 1.


% Robot delivers product that is not requested at picking stations
err(deliver, noOrder, (R, T)) :-     occurs(object(robot,           R ), action(deliver,         (O, P, _)), T  );
                                     holds( object( robot,          R ), value( at,              (X, Y)   ), T-1);
                                     holds( object( pickingStation, PS), value( at,              (X, Y)   ), T-1);
                                     holds( object(order,           O ), value( pickingStation,  PS       ), T-1);
                                 not holds(object(order,            O ), value( line,            (P, _)   ), T-1).

% Robot delivers higher amount than requested
err(deliver, orderAmount, (R, T)) :- occurs(object(robot, R), action(deliver, (O, P, Q)), T);
                                     holds( object(order, O), value( line,    (P, RQ)  ), T);
                                     Q > RQ.


% - Book-Keeping: Related Inertia Abnormals ---------------------------------------
%
