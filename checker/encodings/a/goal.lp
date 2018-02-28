% = GOAL CONDITION =============================================================

err(goal, unfilledOrder, (O, P, Q, H)) :- holds(object(order, O), value(line, (P, Q)), H);
                                          horizon(H).
