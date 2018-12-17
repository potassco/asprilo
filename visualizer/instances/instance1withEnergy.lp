#program base.

%constants
#const grid_x = 3.
#const grid_y = 3.

init(object(node, (Y-1) * grid_x + X), value(at, (X, Y))) :- X=1..grid_x, Y=1..grid_y.

timelimit(8).

%init
%init robots
init(object(robot, 1), value(at, (1, 1))).
init(object(robot, 1), value(max_energy, 20)).
init(object(robot, 1), value(energy, 16)).

%init energy cost
init(object(robot, 1), value(energy_cost, (move, 1))).
init(object(robot, 1), value(energy_cost, (pickup, 3))).
init(object(robot, 1), value(energy_cost, (putdown, 2))).
init(object(robot, 1), value(energy_cost, (deliver, 0))).

%init shelves
init(object(shelf, 1), value(at, (3, 1))).

%init picking stations
init(object(pickingStation, 1), value(at, (3, 3))).

%init charging stations
init(object(chargingStation, 1), value(at, (1,1))).

%init products
init(object(product, 1), value(on, (1, 280))).

%init requests
init(object(order, 1), value(line, (1, 2))).
init(object(order, 1), value(pickingStation, 1)).

