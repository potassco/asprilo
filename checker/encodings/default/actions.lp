#include "./instance.lp".

% = ACTIONS=====================================================================


% - Domain ---------------------------------------------------------------------

action(move(0,1)).
action(move(1,0)).
action(move(0,-1)).
action(move(-1,0)).
action(pickup).
action(putdown).
action(deliver(O, A, Q)) :- init(object(order, O), value(line, (A, RQ))),
                            Q = 1..RQ . % RQ and Q are the requested
                                        % and delivered quantity, resp.

% -- Inertia -------------------------------------------------------------------

holds(F, T) :- holds(F, T-1), not abnormal(F, T).









