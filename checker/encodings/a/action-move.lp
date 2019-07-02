% = ACTION move ================================================================

% - Domain ---------------------------------------------------------------------

action(move, (0,1)).
action(move, (1,0)).
action(move, (0,-1)).
action(move, (-1,0)).


% - Checks: Preconditions ------------------------------------------------------

% Target node non-existent
err(move, node, (R, T))   :-     occurs(object(robot, R), action(move, (DX,    DY)),  T  );
                                 holds( object(robot, R), value(at,    (X,      Y)),  T-1);
                             not holds( object(node,  _), value(at,    (X+DX, Y+DY)), T  ).

% Movement domain violated
err(move, domain, (R, T)) :-     occurs(object(robot, R), action(move, (DX,    DY)),  T  );
                                 holds( object(robot, R), value(at,    (X,      Y)),  T-1);
                             not action(move, (DX, DY)).



%adjacent(R, DX, DY, T) :- holds( object(node,  _), value(at,    (X+DX, Y+DY)), T  ).at(robot(R), X, Y, T-1); node(X+DX, Y+DY); action(move(DX, DY)).

% - Book-Keeping: Effects --------------------------------------------------------------------

holds(object(robot, R), value(at, (X+DX, Y+DY)), T) :- occurs(object(robot, R), action(move,   (DX, DY)), T  );
                                                       holds( object(robot, R), value(at,      (X, Y)),   T-1).

holds(object(shelf, S), value(at, (X,    Y   )), T) :- holds( object(robot, R), value(at,      (X, Y)),   T  );
                                                       holds( object(robot, R), value(carries,     S),   T-1).


% - Book-Keeping: Related Inertia Abnormals ---------------------------------------

ab(object(robot, R), value(at, (X, Y)), T) :- holds( object(robot, R), value(at,      (X, Y)), T-1);
                                              occurs(object(robot, R), action(move,        _), T  ).
ab(object(shelf, S), value(at, (X, Y)), T) :- holds( object(shelf, S), value(at,      (X, Y)), T-1);
                                              occurs(object(robot, R), action(move,        _), T  );
                                              holds( object(robot, R), value(carries,      S), T-1).
