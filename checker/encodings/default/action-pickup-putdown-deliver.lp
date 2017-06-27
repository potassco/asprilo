% = ACTION: PICKUP, PUTDOWN, DELIVER ===========================================


% - Domain ---------------------------------------------------------------------

action(pickup).
action(putdown).
action(deliver(O, A, Q)) :- init(object(order, O), value(line, (A, RQ))),
                            Q = 1..RQ . % RQ and Q are the requested
                                        % and delivered quantity, resp.

% - Preconditions - Verification -----------------------------------------------

% Pickup: no shelf to pickup at location
err(pickup(1), R, T)  :- at(robot(R), X, Y, T-1); not at(shelf(_), X, Y, T-1);
                         occurs(object(robot, R), action(pickup, ()), T).

% Pickup: robot already carries a shelf
err(pickup(2), R, T)  :- carries(R, _, T-1); occurs(object(robot, R), action(pickup, ()), T).

% Putdown: robot does not carry a shelf
err(putdown(1), R, T) :- not carries(R, _, T-1); occurs(object(robot, R), action(putdown, ()), T).

% Putdown: robot tries to putdown shelf on highway node
err(putdown(2), R, T) :- at(robot(R), X, Y, T-1); highway(X, Y); occurs(object(robot, R), action(putdown, ()), T).


% Deliver: robot not at picking station
err(deliver(1), R, T) :- at(robot(R), X, Y, T-1); not at(station(_), X, Y, T-1);
                         occurs(object(robot, R), action(deliver, (_, _, _)), T).

% Deliver: robot not carrying a shelf
err(deliver(2), R, T) :- not carries(R, _, T); occurs(object(robot, R), action(deliver, (_, _, _)), T).


% Deliver: robot delivers product that is not requested at picking stations
err(deliver(3), R, T) :- at(robot(R), X, Y, T-1); at(station(P), X, Y, T-1);
                         not open(_, A, _, T-1); assigned(O, P);
                         occurs(object(robot, R), action(deliver, (O, A, _)), T).

% Deliver: robot delivers higher amount than requested
err(deliver(4), R, T) :- at(robot(R), X, Y, T-1); open(_, A, RQ, T-1);
                         occurs(object(robot, R), action(deliver, (P, A, Q)), T); Q > RQ.


% - Effects --------------------------------------------------------------------


carries(R, S, T)      :- at(robot(R), X, Y, T-1); at(shelf(S), X, Y, T-1);
                         occurs(object(robot, R), action(pickup, ()), T).

open(O, A, RQ-Q, T)   :- open(O, A, RQ, T); occurs(object(robot, R), action(deliver, (O, A, Q)), T); RQ < Q.

% - Inertia --------------------------------------------------------------------

carries(R, S, T)     :-  carries(R, S, T-1); not occurs(object(robot, R), action(putdown, ()), T).

% - Static Laws - Verification -------------------------------------------------

% An order must be assigned to exactly one picking stations
err(assigned(1), O) :- { assigned(O, _) } > 1; order(O).
