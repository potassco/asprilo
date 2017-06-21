#program base.

init(object(node, 0), value(at, (1,1))) :- vertice(0).

sizeX(SizeX) :- SizeX = #max{ X : init(object(node, N2), value(at, (X,_)))}.
sizeY(SizeY) :- SizeY = #max{ Y : init(object(node, N2), value(at, (_,Y)))}.
:- sizeX(SizeX), sizeY(SizeY), SizeY > SizeX.

1{init(object(node, N2), value(at, (X+1,Y))); 
  init(object(node, N2), value(at, (X,Y+1)))}1 :- init(object(node, N), value(at, (X,Y))), edge(N, N2), N < N2, X < 100, Y < 100, X > 0, Y > 0.
1{init(object(node, N2), value(at, (X-1,Y))); 
  init(object(node, N2), value(at, (X,Y-1)))}1 :- init(object(node, N), value(at, (X,Y))), edge(N, N2), N > N2, X < 100, Y < 100, X > 0, Y > 0.

:- not init(object(node, N), value(at, (_,_))),  vertice(N).
:- init(object(node, N), value(at, (X,Y))), init(object(node, N2), value(at, (X,Y))), N != N2.
:- init(object(node, N), value(at, (X,Y))), init(object(node, N), value(at, (X2,Y2))), X != X2, Y != Y2.
:- init(object(node, N), value(at, (X,Y))), init(object(node, N2), value(at, (X+1,Y))), N2 - N != 1.

init(object(robot, Robot_ID), value(at, (X, Y))) :- agent(Robot_ID, Node_ID, _), init(object(node, Node_ID), value(at, (X,Y))).
init(object(shelf, Node_ID), value(at, (X, Y))) :- init(object(node, Node_ID), value(at, (X,Y))), pods(Node_ID).

time_1(T) :- path(_, _, T, _).
time_2(T) :- path(_, _, _, T).

time(1, 0, 1).
time(T + 1, T1 + 1, T2) :- time(T, T1, T2), path(_, _, T1 + 1, T2), time_1(T1), time_2(T2).
time(T, 0, T2 + 1) :- time(T, T1, T2), path(_, _, 0, T2 + 1), not path(_, _, T1 + 1, T2), time_1(T1), time_2(T2).
time(T) :- time(T, T1, T2).

at(Robot_ID, X, Y, 0) :- init(object(robot, Robot_ID), value(at, (X, Y))).

at(Robot_ID, X, Y, T) :- path(Robot_ID, Node_ID, T1, T2),
                         time(T, T1, T2),
                         init(object(node, Node_ID), value(at, (X,Y))).

at_change(Robot_ID, T) :- at(Robot_ID, X, Y, T-1), at(Robot_ID, X2, Y2, T), |X2-X|+|Y2-Y| > 0.

at(Robot_ID, X, Y, T) :- not path(Robot_ID, _, T1, T2),
			 not at_change(Robot_ID, T),
                         time(T, T1, T2),
                         at(Robot_ID, X, Y, T-1).

occurs(object(robot, Robot_ID), action(move, (X2-X, Y2-Y)), T) :- at(Robot_ID, X, Y, T-1), at(Robot_ID, X2, Y2, T), |X2-X|+|Y2-Y| > 0.

init(object(checkpoint, Node_ID), value(at, (X, Y))) :- store(ID, Node_ID), init(object(node, Node_ID), value(at, (X,Y))).
init(object(checkpoint, Node_ID), value(checkpoint, (s, ID, 0))) :- store(ID, Node_ID), init(object(node, Node_ID), value(at, (X,Y))).

init(object(checkpoint, Node_ID), value(at, (X, Y))) :- goal(_, ID, Node_ID, _), init(object(node, Node_ID), value(at, (X,Y))).
init(object(checkpoint, Node_ID), value(checkpoint, (g, ID, 1))) :- goal(_, ID, Node_ID, _), init(object(node, Node_ID), value(at, (X,Y))).

init(object(checkpoint, Node_ID), value(at, (X, Y))) :- depot(ID, Node_ID), init(object(node, Node_ID), value(at, (X,Y))).
init(object(checkpoint, Node_ID), value(checkpoint, (d, ID, 2))) :- depot(ID, Node_ID), init(object(node, Node_ID), value(at, (X,Y))).

init(object(task, Task_ID), value(checkpoint, (Node_ID, s, 0))) :- store(Task_ID, Node_ID).
init(object(task, Task_ID), value(checkpoint, (Node_ID, g, 1))) :- goal(_, Task_ID, Node_ID, _).
init(object(task, Task_ID), value(checkpoint, (Node_ID, d, 2))) :- depot(Task_ID, Node_ID).

init(object(task, Task_ID), value(type, Task_Type)) :- task(Task_ID, _, _ , Task_Type).
init(object(task, Task_ID), value(group, Task_Group)) :- task(Task_ID, Task_Group, _ , _).
init(object(task, Task_ID), value(robot, Robot_ID)) :- goal(Robot_ID, Task_ID, _, _).
