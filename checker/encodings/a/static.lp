% = STATIC LAWS ================================================================

% - Verification of Object Locations --------------------------------------

% At most one object of the same type (robot. shelf, picking station, etc.)  may occupy a node at
% the same time, otherwise collision.
err(static, collNode, (OT, X, Y, T))      :- { holds(object(OT, _),     value(at, (X, Y)), T) } > 1;
                                             holds(object(node, _), value(at, (X, Y)),     T);
                                             init( object(OT,   _), _);
                                             time(T).


% Two adjacent objects of the same type (robots, shelves) must not swap places in one step, i.e,
% they would collide.
err(static, collSwap, (OT, R1, R2, T))    :- holds(object(OT, R1), value(at, (X1, Y1)), T);
                                             holds(object(OT, R2), value(at, (X2, Y2)), T);
                                             holds(object(OT, R1), value(at, (X2, Y2)), T-1);
                                             holds(object(OT, R2), value(at, (X1, Y1)), T-1);
                                             R1<R2, |X2-X1|+|Y2-Y1|==1.

% An object can only be at one postion at the same time.
err(static, twoPos, (OT,O, T))            :-  { holds(object(OT,   O), value(at, (X, Y)), T) :
                                                holds(object(node, _), value(at, (X, Y)), T)   } > 1;
                                              init(object(OT,   O), _);
                                              time(T).

%  An object can only do one action at a time.
err(static, multActions, (OT, O, T))      :-  { occurs(object(OT, O), _, T) } > 1;
                                              init(object(OT, O), _);
                                              time(T).

% A robot must never place a shelves on a highway node.
err(static, highwayPutdown, (R, X, Y, T)) :- holds( object(highway, _), value(at, (X, Y)),   T);
                                             holds( object(robot, R),   value(at, (X, Y)),   T);
                                             occurs(object(robot, R),   action(putdown, ()), T);
                                             time(T).

% An order must be assigned to exactly one picking stations
err(static, assigned, O)                  :- { holds(object(order, O), value(pickingStation, _), T) } > 1;
                                             holds(object(order, O), _, T);
                                             time(T).
err(static, assigned, O)                  :- { holds(object(order, O), value(pickingStation, _), T) } < 1;
                                             holds(object(order, O), _, T);
                                             time(T).
