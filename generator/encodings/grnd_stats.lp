% = GROUNDING SIZE STATS ENCODING ==================================================================

stats(rule,        N) :- N = #count{ C,H,B:    o(rule(C,H,B)) },               N > 0.
stats(weight_rule, N) :- N = #count{ C,H,LB,B: o(weight_rule(C,H,LB,B)) },     N > 0.
stats(minimize,    N) :- N = #count{ P,L:      o(minimize(P,L)) },             N > 0.
stats(project,     N) :- N = #count{ L:        o(project(L)) },                N > 0.
stats(output_atom, N) :- N = #count{ S:        o(output_atom(S)) },            N > 0.
stats(output_term, N) :- N = #count{ S,C:      o(output_term(S,C)) },          N > 0.
stats(assume,      N) :- N = #count{ L:        o(assume(L)) },                 N > 0.

stats_total(       S) :- S = #sum{   N,T:      stats(T,N) },                   S > 0.
