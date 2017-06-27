% = PLAN REPRESENTAITON ========================================================

horizon(H) :- H = #max{0; T : occurs( _, _, T)}
time(1..H) :-  horizon(H).

#include "./action-move.lp".
#include "./action-pickup-putdown-deliver.lp".
#include "./goal.lp"
