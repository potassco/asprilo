% = ACTION: PICKUP, PUTDOWN, DELIVER ===========================================


% - Domain ---------------------------------------------------------------------

action(putdown, ()).


% - Preconditions - Verification -----------------------------------------------

% Robot does not carry a shelf
err(putdown, noShelf, (R, T)) :-     occurs(object(robot, R), action(putdown, ()),   T  );
                                 not holds( object(robot, R), value(carries,   _),   T-1).


% - Book-Keeping: Effects --------------------------------------------------------------------
%
%   None.


% - Book-Keeping: Related Inertia Abnormals ---------------------------------------

ab(object(robot, R), value(carries, S), T) :-  occurs(object(robot, R), action(putdown, ()), T  );
                                               holds( object(robot, R), value(carries,   S), T-1).
