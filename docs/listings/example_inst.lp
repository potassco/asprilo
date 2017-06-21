%
% Warehouse with 5 x 5 recangular footprint
%
%% init(object(grid,1), value(xsize, 10)).
%% init(object(grid,1), value(ysize, 10)).
%
% expanded to

init(object(node,1),value(at,(1,1))).
init(object(node,2),value(at,(2,1))).
init(object(node,3),value(at,(3,1))).
init(object(node,4),value(at,(4,1))).
init(object(node,5),value(at,(5,1))).
init(object(node,6),value(at,(1,2))).
init(object(node,7),value(at,(2,2))).
init(object(node,8),value(at,(3,2))).
init(object(node,9),value(at,(4,2))).
init(object(node,10),value(at,(5,2))).
init(object(node,11),value(at,(1,3))).
init(object(node,12),value(at,(2,3))).
init(object(node,13),value(at,(3,3))).
init(object(node,14),value(at,(4,3))).
init(object(node,15),value(at,(5,3))).
init(object(node,16),value(at,(1,4))).
init(object(node,17),value(at,(2,4))).
init(object(node,18),value(at,(3,4))).
init(object(node,19),value(at,(4,4))).
init(object(node,20),value(at,(5,4))).
init(object(node,21),value(at,(1,5))).
init(object(node,22),value(at,(2,5))).
init(object(node,23),value(at,(3,5))).
init(object(node,24),value(at,(4,5))).
init(object(node,25),value(at,(5,5))).


%
% "Outer ring" is a highway
%
init(object(highway,1),value(at,(1,1))).
init(object(highway,2),value(at,(2,1))).
init(object(highway,3),value(at,(3,1))).
init(object(highway,4),value(at,(4,1))).
init(object(highway,5),value(at,(5,1))).
init(object(highway,6),value(at,(1,2))).
init(object(highway,10),value(at,(5,2))).
init(object(highway,11),value(at,(1,3))).
init(object(highway,15),value(at,(5,3))).
init(object(highway,16),value(at,(1,4))).
init(object(highway,20),value(at,(5,4))).
init(object(highway,21),value(at,(1,5))).
init(object(highway,22),value(at,(2,5))).
init(object(highway,23),value(at,(3,5))).
init(object(highway,24),value(at,(4,5))).
init(object(highway,25),value(at,(5,5))).


%
% Shelves
%

% Shelf 1: location & class
init(object(shelf, 1), value(class, 2)).
init(object(shelf, 1), value(at, (2,3))).

% Shelf 2: location & class
init(object(shelf, 2), value(class, 1)).
init(object(shelf, 2), value(at, (3,3))).

% Shelf 3: location & class
init(object(shelf, 3), value(class, 1)).
init(object(shelf, 3), value(at, (4,3))).

% Shelf class 1: shelf 2 and 3 are both of class 1 that stipulates their maximum capacity
% wrt. quantity, weight and volume
init(object(shelf_class, 1), value(maxQuantity, 20)).
init(object(shelf_class, 1), value(maxWeight, 250)).
init(object(shelf_class, 1), value(maxVolume, 400)).

% Shelf class 2: shelf 1 is of class 1 that stipulates its maximum capacity
% wrt. quantity, weight and volume
init(object(shelf_class, 2), value(maxQuantity, 40)).
init(object(shelf_class, 2), value(maxWeight, 500)).
init(object(shelf_class, 2), value(maxVolume, 1000)).


%
% Picking Stations
%

% Picking Station 1: location and class
init(object(pickingStation, 1), value(class, 1)).
init(object(pickingStation, 1), value(at, (2,1))).

% Picking Station 2: location and class
init(object(pickingStation, 2), value(class, 1)).
init(object(pickingStation, 2), value(at, (4,1))).

% Picking Station class 1: pickinstations 1 and 2 are both of class 1 that stipulates
% a maximum quantitative capacity of 20
init(object(pickingStation_class, 1), value(maxQuantity, 20)).


%
% Charging Stations
%
% Charging Station 1: location
init(object(chargingStation, 1), value(at, (1,5))).


%
% Robots
%

% Robot 1: location and class
init(object(robot, 1), value(class, 1)).
init(object(robot, 1), value(at, (1,5))).

% Robot 2: location and class
init(object(robot, 2), value(class, 1)).
init(object(robot, 2), value(at, (2,5))).

% Robot class 1: to which robot 1 and 2 belong
init(object(robot_class, 1), value(maxWeight, 100)).
init(object(robot_class, 1), value(maxEnergy, 25)).

% Robot 3: location and direct definition of further properties w/o using class membership
init(object(robot, 3), value(at, (3,5))).
init(object(robot, 3), value(maxWeight, 300)).
init(object(robot, 3), value(maxEnergy, 75)).


%
% Orders
%

% Order 1:
% - requests 5 x product 1 and 3 x product 2
% - arrives at time point 1, and expires at time point 8
init(object(order, 1), value(line, (1, 5))).
init(object(order, 1), value(line, (2, 3))).
init(object(order, 1), value(arrivalDate, 1)).
init(object(order, 1), value(expirationDate, 8)).

% Order 2:
% - requests 1 x product 3
% - arrives at time point 5, and expires at time point 10
init(object(order, 2), value(line, (3, 1))).
init(object(order, 2), value(line, (3, 1))).
init(object(order, 2), value(arrivalDate, 5)).
init(object(order, 2), value(expirationDate, 10)).
