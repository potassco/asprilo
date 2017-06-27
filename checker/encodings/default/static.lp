% STATIC LAWS ==================================================================

% Only one robot (shel1f) at a node at the same time.
%% err(static(1),(X,Y)) :- node(X,Y), { at(robot(R), X, Y , T) : robot(R) } > 1.
%% err(static(2),(X,Y)) :- node(X,Y), { at(shelf(S),  X, Y ,T) : shelf(S) } > 1.

%% %       A robot/shelf can only be at one node at a time.
%% :-      robot(RID), 2{holds(at(robot(RID),node(X,Y)),t) : node(X,Y)}.
%% :-      shelf(SID), 2{holds(at(shelf(SID),node(X,Y)),t) : node(X,Y)}.

%% %       Two robots can't swap places as they would crash.
%% :-      holds(at(robot(RID1),node(X1,Y1)),t), holds(at(robot(RID2),node(X2,Y2)),t),
%%         holds(at(robot(RID1),node(X2,Y2)),t-1), holds(at(robot(RID2),node(X1,Y1)),t-1),
%%         RID1<RID2, |X2-X1|+|Y2-Y1|==1.

%% %       On higway nodes shelfs can't be putdown and robots can't do nothing for more than one time step.
%% :-  highway(X,Y), not node(X,Y).
%% :-  highway(X,Y), holds(at(robot(RID),node(X,Y)),t), occ(robot(RID),putdown,t).
%% :-  highway(X,Y), holds(at(robot(RID),node(X,Y)),t), not moved(robot(RID),t-1), not moved(robot(RID),t).

%% %       Small scope loop preventions preventing opposite actions at adjacent time points.
%% :- occ(robot(RID),move(DX,DY),t), occ(robot(RID),move(-DX,-DY),t-1).
%% :- occ(robot(RID),pickup,t), occ(robot(RID),putdown,t-1).
%% :- occ(robot(RID),putdown,t), occ(robot(RID),pickup,t-1).
