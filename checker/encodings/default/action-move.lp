% = ACTION: MOVEMENT ===========================================================


% - Domain ---------------------------------------------------------------------

action(move(0,1)).
action(move(1,0)).
action(move(0,-1)).
action(move(-1,0)).


% - Preconditions - Verification -----------------------------------------------

% Target node not adjacent to robot
adjacent(R, DX, DY, T) :- at(robot(R), X, Y, T-1); node(X+DX, Y+DY); action(move(DX, DY)).
err(move(1), R, T)     :- occurs(object(robot, R), action(move, (DX, DY)), T); not adjacent(R, DX, DY, T).

% Target node occupied by other robot
err(move(2), R, T)     :- occurs(object(robot, R), action(move, (DX, DY)), T); at(robot(R), X, Y, T-1);
                          { at(robot(_), X+DX, Y+DY, T) } > 1.


% - Effects --------------------------------------------------------------------

at(robot(R), X+DX, Y+DY, T) :- occurs(object(robot, R), action(move, (DX, DY)), T);
                               at(robot(R), X, Y, T-1); node(X+DX, Y+DY).
at(shelf(S),    X,    Y, T) :- at(robot(R), X, Y, T), carries(R, S, T-1).

moves(robot(R), T)          :- occurs(object(robot, R), action(move, _), T). % aux pred

% - Inertia --------------------------------------------------------------------

at(robot(R), X, Y, T) :- at(robot(R), X, Y, T-1); not moves(robot(R), T); time(T).
at(shelf(R), X, Y, T) :- at(shelf(R), X, Y, T-1); not moves(robot(R), T); time(T); carries(R, S, T-1).


% - Static Laws - Verification -------------------------------------------------

% At most one robot (shelf) may occupy a node at the same time.
err(at(1), (X, Y), T)   :- { at(robot(_), X, Y, T) } > 1; node(X, Y); time(T).
err(at(2), (X, Y), T)   :- { at(shelf(_), X, Y, T) } > 1; node(X, Y); time(T).

% Two adjacent robots must not swap places in one step, i.e, they would collide.
err(at(3), (R1, R2), T) :- at(robot(R1), X1, Y1,   T), at(robot(R2), X2, Y2,    T),
                             at(robot(R1), X2, Y2, T-1), at(robot(R2), X1, Y1 , T-1),
                             R1<R2, |X2-X1|+|Y2-Y1|==1.
