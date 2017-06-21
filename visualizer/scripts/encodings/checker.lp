#program base.

%%    ACTIONS
action(move, (0,1)).
action(move, (1,0)).
action(move, (0,-1)).
action(move, (-1,0)).
action(pickup, ()).
action(putdown, ()).
action(deliver, (OID, PRID, AMT)) :- init(object(order, OID), value(line, (PRID, OAMT))), AMT = 1..OAMT.

%%  INITIAL STATE
holds(Object, Value, 0) :- init(Object, Value).

%%  INERTIA
%       Everything that does not change remains the same.
holds(Object, Value, T) :- holds(Object, Value, T-1), not ab(Object, Value, T), time(T).

object(Object, ID) :- init(object(Object, ID), Value).
object(Object) :- object(Object, ID).
node(X, Y) :- init(object(node, _), value(at, (X, Y))).

%       Get the plan length from the occurs.
time(T+1) :- occurs(_, _, T).
time(T-1) :- time(T), T > 0. 

%%    ACTION - PRECONDITIONS
%       Move: The destination node must exist.
poss(object(robot, RID), action(move, (DX,DY)), T) :- action(move, (DX,DY)),
                                                      holds(object(robot, RID), value(at, (X, Y)), T),
                                                      node(X+DX,Y+DY), 
                                                      time(T).

%       Pickup: There must be a shelf on the same node as the robot at the same time and the robot don´t carries the shelf already.
poss(object(robot, RID), action(pickup, ()), T) :-  holds(object(robot, RID), value(at, (X, Y)), T),
                                                    holds(object(shelf, SID), value(at, (X, Y)), T),
                                                    not holds(object(robot, RID), value(carries, SID), T),
                                                    time(T).


%       Putdown: The robot must carrie a shelf.
poss(object(robot, RID), action(putdown, ()), T) :- holds(object(robot, RID), value(carries, _), T),
                                                    time(T).

%       Deliver: The robot, the shelf, and the picking station must be on the same node, the robot must carrie the shelf, the shelf must contain the delivered 
%                product, the product must be requested by the order and the destination of the order must be the picking station the robot is standing on.
%                The delivered amount must be a value between one and the ordered amount. It also can´t be greather then the amount the shelf carries.
poss(object(robot, RID), action(deliver, (OID, PRID, DAMT)), T) :- 
                                        DAMT =  1..OAMT,
                                        DAMT <= AMT,
                                        holds(object(order, OID), value(line, (PRID, OAMT)), T),
                                        holds(object(order, OID), value(pickingStation, PSID), T),
                                        holds(object(product, PRID), value(on, (SID, AMT)), T),
                                        holds(object(shelf, SID), value(at, (X, Y)), T),
                                        holds(object(pickingStation, PSID), value(at, (X, Y)), T),
                                        holds(object(robot, RID), value(at, (X, Y)), T),
                                        holds(object(robot, RID), value(carries, SID), T),
                                        time(T).

%%  ACTION - EFFECTS - holds
%       Moves a robot.
holds(object(robot, RID), value(at, (X + DX, Y + DY)), T + 1) :- holds(object(robot, RID), value(at, (X, Y)), T),
                                                                 occurs(object(robot, RID), action(move, (DX, DY)), T).

%       Moves a shelf to the same position as a robot that carries this shelf.
holds(object(shelf, SID), value(at, (X + DX, Y + DY)), T + 1) :- holds(object(robot, RID), value(at, (X, Y)), T),
                                                                 occurs(object(robot, RID), action(move, (DX, DY)), T),
                                                                 holds(object(robot, RID), value(carries, SID), T).

%       A robot picks up the shelf on the same postion.
holds(object(robot, RID), value(carries, SID), T + 1) :- holds(object(robot, RID), value(at, (X, Y)), T),
                                                         holds(object(shelf, SID), value(at, (X, Y)), T),
                                                         occurs(object(robot, RID), action(pickup, ()), T).

%       If the delivered amount is lower then the amount of products carried by the shelf the carried amount is reduced.
holds(object(product, PRID), value(on, (SID, AMT-DAMT)), T + 1) :- AMT > DAMT,
                                                                   holds(object(product, PRID), value(on, (SID, AMT)), T),
                                                                   holds(object(robot, RID), value(carries, SID), T),
                                                                   occurs(object(robot, RID), action(deliver, (OID, PRID, DAMT)), T).                

%       If the delivered amount is lower then the ordered amount the order is partially fulfilled. The ordered amount is reduced.
holds(object(order, OID), value(line, (PRID, OAMT-DAMT)), T + 1) :- DAMT < OAMT,
                                                                    holds(object(order, OID), value(line, (PRID, OAMT)), T),
                                                                    occurs(object(robot, RID), action(deliver, (OID, PRID, DAMT)), T).  
            
%       If delivered amount and ordered amount are the same the order is done.
holds(object(order, OID), value(done, (PRID)), T + 1) :- holds(object(order, OID), value(line, (PRID, OAMT)), T),
                                                         occurs(object(robot, RID), action(deliver, (OID, PRID, OAMT)), T). 

%%	ABNORMALS
%       Anything that changes is abnormal and won't be handled by inertia.
%       A robot has been moved.
ab(object(robot, RID), value(at, (X, Y)), T + 1) :- holds(object(robot, RID), value(at, (X, Y)), T),
                                                    occurs(object(robot, RID), action(move, (_, _)), T).
%       A shelf has been moved.
ab(object(shelf, SID), value(at, (X, Y)), T + 1) :- holds(object(robot, RID), value(at, (X, Y)), T),
                                                    occurs(object(robot, RID), action(move, (DX, DY)), T),
                                                    holds(object(robot, RID), value(carries, SID), T).
%       A shelf has been put down.
ab(object(robot, RID), value(carries, SID), T + 1) :- holds(object(robot, RID), value(carries, SID), T),
                                                      occurs(object(robot, RID), action(putdown, ()), T).

%       Products has been removed from a shelf.
ab(object(product, PRID), value(on, (SID, AMT)), T + 1) :- ab(object(product, PRID), value(on, (SID, AMT)), T + 1),
                                                           holds(object(robot, RID), value(carries, SID), T),
                                                           occurs(object(robot, RID), action(deliver, (_, PRID, DAMT)), T).  

ab(object(order, OID), value(line, (PRID, OAMT)), T + 1) :- holds(object(order, OID), value(line, (PRID, OAMT)), T),
                                                            occurs(object(robot, RID), action(deliver, (OID, PRID, DAMT)), T). 

%%    STATIC LAWS
%       There can only be one object of the same kind at a node at the same time.
error(collide, (Object, node(X,Y)), T) :-  2{holds(object(Object, ID), value(at, (X, Y)), T) : object(Object, ID)}, object(Object), node(X,Y), time(T).
%       An object can only be at one node at a time.
error(doubleObject, (Object, ID), T) :-  2{holds(object(Object, ID), value(at, (X, Y)), T) : node(X,Y)}, object(Object, ID), object(Object), time(T).

%       An object can only do one action at a time.
error(doubleAction, (Object, ID), T) :-  2{occurs(object(Object, ID), A, T) : object(Object, ID)}, object(Object, ID), time(T).

%       An robot can only do one action if it is possible.
error(invalidAction, (robot, RID, A), T) :- occurs(object(robot, RID), A, T), not poss(object(robot, RID), A, T).

%       Two robots can't swap places as they would crash.
error(invalidSwap, (RID1, RID2), T) :- holds(object(robot, RID1), value(at, (X1, Y1)), T),   holds(object(robot, RID2), value(at, (X2, Y2)), T),
                                       holds(object(robot, RID1), value(at, (X2, Y2)), T-1), holds(object(robot, RID2), value(at, (X1, Y1)), T-1),
                                       RID1<RID2, |X2-X1|+|Y2-Y1|==1, time(T).

%       Robots can´t putdown shelves on highways.
error(invalidPutdown, (RID, node(X, Y)), T) :- holds(object(highway, _), value(at, (X, Y)), T), 
                                               holds(object(robot, RID), value(at, (X, Y)), T), 
                                               occurs(object(robot, RID), action(putdown, ()), T),
                                               time(T).

%       Robots can´t standing still on highways too long.
error(blockHighway, (RID, node(X, Y)), T) :-  holds(object(highway, _), value(at, (X, Y)), T), 
                                              holds(object(highway, _), value(at, (X, Y)), T-1), 
                                              holds(object(highway, _), value(at, (X, Y)), T-2), 
                                              holds(object(robot, RID), value(at, (X, Y)), T), 
                                              holds(object(robot, RID), value(at, (X, Y)), T-1),
                                              holds(object(robot, RID), value(at, (X, Y)), T-2),
                                              not occurs(object(robot, RID), action(deliver, (_, _, _)), T),
                                              not occurs(object(robot, RID), action(deliver, (_, _, _)), T-1),
                                              not occurs(object(robot, RID), action(deliver, (_, _, _)), T-2).

%%	GOAL - CONDITION
%       The goal is reached when all orders are done.
error(openOrder, (OID, PRID), 0) :- init(object(order, OID), value(line, (PRID, OAMT))), not holds(object(order, OID), value(done, (PRID)), _).

:- error(_,_,_).
%#show error/3.
