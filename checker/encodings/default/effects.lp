% = ACTION EFFECTS =============================================================
%
% This takes the plan facts, i.e., occurs/3 facts directly into account.


% - Movement -------------------------------------------------------------------

at(robot(R), X+DX, Y+DY, T) :- node(X+DX, Y+DY), at(robot(R), X, Y, T-1),
                               occurs(object(robot, R), value(move, (DX, DY)), T).
at(shelf(S),    X,    Y, T) :- at(robot(R), X, Y, T), holds(carries(R, S),T-1).
moved(robot(RID),t)         :-  occ(robot(RID),move(_,_),t), robot(RID).


% - Carrying -------------------------------------------------------------------

holds(carries(RID,SID),t)                       :-      holds(at(robot(RID),node(X,Y)),t),
                                                        holds(at(shelf(SID),node(X,Y)),t),
                                                        occ(robot(RID),pickup,t).
