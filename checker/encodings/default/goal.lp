% = GOAL CONDITION =============================================================

err(openOrder, (O, P, Q), H) :- holds(object(order, O), value(line, (P, Q)), H);
                                horizon(H).
