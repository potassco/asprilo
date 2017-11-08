% = ORDER FULFILLMENT ==============================================================================
%
%   Sequence of actions and conditions required to fulfill (i.e., fully process) an order.
%

% Remove outdated order lines
ab(object(order,   O), value(line, (P, RQ)), T) :-  occurs(object(robot,   R), action(deliver, (O, P, _)), T  );
                                                    holds( object(order,   O), value( line,    (P, RQ)  ), T-1).
