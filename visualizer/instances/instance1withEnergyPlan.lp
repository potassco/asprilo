%plan
occurs(object(robot, 1), action(move,(1,0)), 1).
occurs(object(robot, 1), action(move,(1,0)), 2).
occurs(object(robot, 1), action(pickup,()), 3).
occurs(object(robot, 1), action(move,(0,1)), 4).
occurs(object(robot, 1), action(move,(0,1)), 5).
occurs(object(robot, 1), action(deliver,(1,1,2)), 6).

occurs(object(robot, 1), action(move,(0,-1)), 7).
occurs(object(robot, 1), action(move,(0,-1)), 8).
occurs(object(robot, 1), action(putdown,()), 9).
occurs(object(robot, 1), action(move,(-1,0)), 10).
occurs(object(robot, 1), action(move,(-1,0)), 11).
occurs(object(robot, 1), action(charge,(17)), 12).
