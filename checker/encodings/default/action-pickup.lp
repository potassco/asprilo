% = ACTION: PICKUP, PUTDOWN, DELIVER ===========================================


% - Domain ---------------------------------------------------------------------

action(pickup, ()).


% - Preconditions - Verification -----------------------------------------------

% No shelf to pickup at location
err(pickup, noShelf, (R, T))  :-     occurs(object(robot, R), action(pickup, ()),  T);
                                     holds( object(robot, R), value(at, (X, Y)), T-1);
                                 not holds( object(shelf, _), value(at, (X, Y)), T-1).




% Robot already carries a shelf
err(pickup, carries, (R, T))  :- occurs(object(robot, R), action(pickup, ()), T);
                                 holds(object(R, _), value(carries, _), T-1).


% - Book-Keeping: Effects --------------------------------------------------------------------

holds(object(robot, R), value(carries, S), T) :- occurs(object(robot, R), action(pickup, ()    ), T  );
                                                 holds( object(robot, R),  value(at,     (X, Y)), T-1);
                                                 holds( object(shelf, S),  value(at,     (X, Y)), T-1).


% - Book-Keeping: Related Inertia Abnormals ---------------------------------------
%
%   None.
