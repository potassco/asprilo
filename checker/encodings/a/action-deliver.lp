% = ACTION: PICKUP, PUTDOWN, DELIVER ===========================================


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
err(deliver, noShelf, (R, T)) :-  occurs(object(robot, R), action(deliver, (_, _, _)), T);
                                  { holds( object(robot, R), value( carries, S ), T-1) :
                                    holds( object(shelf, S), _                  , T-1) } < 1.

% Robot delivers product that is not requested at picking stations
err(deliver, noOrder, (R, T)) :-     occurs(object(robot,           R ), action(deliver,         (O, P, _)), T  );
                                     holds( object( robot,          R ), value( at,              (X, Y)   ), T-1);
                                     holds( object( pickingStation, PS), value( at,              (X, Y)   ), T-1);
                                   { holds( object(order,           O ), value( pickingStation,  PS       ), T-1);
                                     holds( object(order,           O ), value( line,            (P, _)   ), T-1) } < 2.

% Robot delivers higher amount than requested
err(deliver, orderAmount, (R, T)) :- occurs(object(robot, R), action(deliver, (O, P, Q)), T);
                                     holds( object(order, O), value( line,    (P, RQ)  ), T-1);
                                     Q > RQ.

% Robot delivers higher amount than available on shelf
err(deliver, shelfAmount, (R, T)) :- occurs(object(robot, R),   action(deliver, (O, P, Q)), T);
                                     holds( object(robot, R),   value(carries,  S        ), T-1);
                                     holds( object(product, P), value(on,     (S, SQ)  )  , T-1);
                                     Q > SQ.

% Robot must deliver at least one unit
err(deliver, zeroAmount, (R, T))  :- occurs(object(robot, R), action(deliver, (_, _, 0)), T).


% - Book-Keeping: Effects -------------------------------------------------------

% Update order lines
holds(object(order, O), value(line, (P, RQ-Q)), T) :- occurs(object(robot, R), action(deliver, (O, P, Q)), T);
                                                      holds(object(order,O), value(line, (P, RQ)), T-1);
                                                      Q < RQ.
% Update product quantities on shelves

holds(object(product, P), value(on, (S, SQ-Q)), T) :- occurs(object(robot,   R), action(deliver, (_, P, Q)), T  );
                                                      holds( object(robot,   R), value(carries,  S        ), T-1);
                                                      holds( object(product, P), value(on,       (S, SQ)  ), T-1);
                                                      Q < SQ.


% - Book-Keeping: Related Inertia Abnormals ---------------------------------------

% Remove outdated product quantites on shelves
ab(object(product, P), value(on,   (S, SQ)), T) :-  occurs(object(robot,   R), action(deliver, (_, P, _)), T  );
                                                    holds( object(robot,   R), value(carries,  S        ), T-1);
                                                    holds( object(product, P), value(on,       (S, SQ)  ), T-1).
