% = ORDER FULFILLMENT ==============================================================================
%
%   Sequence of actions and conditions required to fulfill (i.e., fully process) an order.
%

% Remove outdated order lines
ab(object(order,   O), value(line, (P, RQ)), T) :-  holds(object(robot,           R ), value(at,                  (X, Y) ),    T  );
                                                    holds(object(pickingStation,  PS), value(at,                  (X, Y) ),    T  );
                                                    holds(object(robot,           R ), value(carries,             S      ),    T  );
                                                    holds(object(product,         P ), value(on,                  (S, _ )),    T  );
                                                    holds(object(order,           O ), value(line,                (P, RQ)),    T-1);
                                                    holds(object(order,           O ), value(pickingStation,      PS     ),    T  ).
