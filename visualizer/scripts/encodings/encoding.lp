%%%%TYPES%%%%
% node(X,Y)
%   Describes a node on the grid where the robots can move.
% highway(X,Y)
%   Highways are special nodes where shelfs can't be put down and robots can't idle for more than one time step.
% robot(RID)
%   The variable for the ID of a robot is generally RID.
% shelf(SID)
%   The variable for the ID of a shelf is generally SID.
% pickingstation(PID)
%   The variable for the ID of a pickingstation is generally PID.
% product(PRID)
%   The variable for the ID of a product is generally PRID.
%
%%%FLUENTS%%%
% at(TYPE(ID),node(X,Y))
%   Describes the current Position of the Object indicated by TYPE(ID).
% carries(RID,SID)
%   Indicates that the robot currently carries the shelf.
% on(PRID,SID,AMT)
%   Indicates that on the shelf is a given amount(AMT) of the product.
% request(RQID,PRID,PID,RQAMT)
%   Represents a request with an ID, the product with an amount and the targeted pickingstation.
% done(RQID,PRID,PID,RQAMT)
%   Indicates that the request is done. Can be expanded with external predicate...
%
%%%ACTIONS%%%
% move(DX,DY)
%   pre: The target node must exist.
%   uncond. eff: The robot moves by (DX,DY).
%   cond. eff: If the robot carries a shelf, then the shelf also moves by (DX,DY).
% pickup
%   pre: A shelf must be at the current position of the robot.
%   uncond. eff: The robot now carries the shelf.
% putdown
%   pre: The robot must currently carry a shelf.
%   uncond. eff: The robot no longer carries the shelf.
%
%%%%%%%%%%%%%

#const incremental = true.
#const maxRQID = 4.

#const istop  = "SAT".
#const imin   = 0.
#const imax   = 50. 

#include <incmode>.
#program base.

%%	ACTIONS
action(move(0,1)).
action(move(1,0)).
action(move(0,-1)).
action(move(-1,0)).
action(pickup).
action(putdown).
action(deliver(RQID, PRID, AMT)) :- init(request(RQID, PRID, StationID, RQAMT)), AMT = 1..RQAMT.

%%  INITIAL STATE
holds(F,0) :- init(F).


%%cast external instance format to internal instance format
node(X,Y) :- init(object(node, ID), value(at, (X, Y))). 
highway(X,Y) :- init(object(highway, ID), value(at, (X, Y))). 
init(at(robot(ID), node(X, Y))) :- init(object(robot, ID), value(at, (X, Y))).
init(at(shelf(ID), node(X, Y))) :- init(object(shelf, ID), value(at, (X, Y))).
init(at(pickingstation(ID), node(X, Y))) :- init(object(pickingStation, ID), value(at, (X, Y))).
init(on(ID, ShelfID, Amount)) :- init(object(product, ID), value(on, (ShelfID, Amount))).
init(request(ID, Item, StationID, Amount)) :- init(object(order, ID), value(line, (Item, Amount))), init(object(order,ID),value(pickingStation, StationID)).
init(carries(RID,SID)) :- init(object(robot, RID), value(carries, SID)).

occurs(robot(RID),move(DX,DY),T) :- occurs(object(robot, RID), action(move, (DX,DY)), T).
occurs(robot(RID),pickup,T) :- occurs(object(robot, RID), action(pickup, ()), T).
occurs(robot(RID),putdown,T) :- occurs(object(robot, RID), action(putdown, ()), T).
occurs(robot(RID),deliver(RQID, PRID, RQAMT),T) :- occurs(object(robot, RID), action(deliver, (RQID, PRID, RQAMT)), T).

robot(Robot) :- init(at(robot(Robot), node(_,_))).
shelf(Shelf) :- init(at(shelf(Shelf), node(_,_))).
pickingstation(Pickingstation) :- init(at(pickingstation(Pickingstation), node(_,_))).
product(Product) :- init(on(Product, _, _)).
%--------------------------------------------------%
#program step(t).
%%cast internal plan format to output plan format
occurs(object(robot, RID), action(move, (DX,DY)), t) :- occurs(robot(RID),move(DX,DY),t).
occurs(object(robot, RID), action(pickup, ()), t) :- occurs(robot(RID),pickup,t).
occurs(object(robot, RID), action(putdown, ()), t) :- occurs(robot(RID),putdown,t).
occurs(object(robot, RID), action(deliver, (RQID, PRID, RQAMT)), t) :- occurs(robot(RID),deliver(RQID, PRID, RQAMT),t).

%%	ACTION - CHOICE
{ occurs(robot(RID),A,t):action(A) } 1 :- robot(RID). 
:- occurs(robot(RID),A,t), not poss(robot(RID),A,t).
%%	ACTION - PRECONDITIONS
%       The preconditions for move(DX,DY), pickup and putdown as described at the top under %%%ACTIONS%%%.
poss(robot(RID),move(DX,DY),t)	    :- 	action(move(DX,DY)),
                                        holds(at(robot(RID),node(X,Y)),t-1),
							            node(X+DX,Y+DY).
poss(robot(RID),pickup,t)       	:-	holds(at(robot(RID),node(X,Y)),t-1),
            							holds(at(shelf(SID),node(X,Y)),t-1),
            							not holds(carries(RID,_),t-1).
poss(robot(RID),putdown,t)	        :-	holds(carries(RID,_),t-1).

poss(robot(RID), deliver(RQID, PRID, RQAMT),t) :- 
                                        RQAMT=1..AMT,
                                        holds(request(RQID,PRID,PSID,_),t-1),
                                        holds(carries(RID,_),t-1),
										holds(on(PRID,SID,AMT),t-1),
										holds(at(shelf(SID),node(X,Y)),t-1),
										holds(at(pickingstation(PSID),node(X,Y)),t-1),
                                        holds(at(robot(RID), node(X,Y)), t-1).

%%	ACTION - EFFECTS
%       The conditional and unconditional effect of move, the effect of pickup.
%       The effect of putdown is realized in the abnormal section as it requires the removal of a fluent.
%       moved is an auxilary predicate for later use, indicating that the robot moved.
holds(at(robot(RID),node(X+DX,Y+DY)),t)	:-	node(X+DX,Y+DY),
										holds(at(robot(RID),node(X,Y)),t-1),
										occurs(robot(RID),move(DX,DY),t).
holds(at(shelf(SID),node(X+DX,Y+DY)),t)	:-	node(X+DX,Y+DY),
										holds(at(robot(RID),node(X,Y)),t-1),
										occurs(robot(RID),move(DX,DY),t),
										holds(carries(RID,SID),t-1).
holds(carries(RID,SID),t)			:-	holds(at(robot(RID),node(X,Y)),t),
										holds(at(shelf(SID),node(X,Y)),t),
										occurs(robot(RID),pickup,t).
moved(robot(RID),t)                 :-  occurs(robot(RID),move(_,_),t), robot(RID).


%% REQUEST-/PRODUCT HANDLING
%       Requests are expected to be done after one timestep in the pickingstation.
%       Depending if there is enough of the product on the shelf the amount is lowered 
%                          or the shelf is emptied and the requested amount is lowered.
holds(on(PRID,SID,AMT-RQAMT),t)		:-	AMT>RQAMT,
										holds(on(PRID,SID,AMT),t-1),
                                        holds(carries(RID,SID),t-1),
                                        occurs(object(robot, RID), action(deliver, (RQID, PRID, RQAMT)), t).

holds(request(RQID,PRID,PSID,RQAMT-AMT),t):-	AMT<RQAMT,
                                        holds(request(RQID,PRID,PSID,RQAMT),t-1),
                                        occurs(object(robot, RID), action(deliver, (RQID, PRID, AMT)), t).

holds(done(RQID,PRID,PSID,RQAMT),t)	:-	holds(request(RQID,PRID,PSID,RQAMT),t-1),
                                        occurs(object(robot, RID), action(deliver, (RQID, PRID, RQAMT)), t).

%--------------------------------------------------%
										
%%	INERTIA
holds(F,t) :- holds(F,t-1), not ab(F,t).

%%	INERTIA - ABNORMALS
%       Anything that changes is abnormal and won't be handled by inertia.
ab(at(robot(RID),node(X,Y)),t) 	:-	holds(at(robot(RID),node(X,Y)),t-1),
								moved(robot(RID),t).								
ab(at(shelf(SID),node(X,Y)),t) 	:-	holds(at(shelf(SID),node(X,Y)),t-1),
								holds(carries(RID,SID),t-1),
								moved(robot(RID),t).
ab(carries(RID,SID),t)		:-	holds(carries(RID,SID),t-1),
								occurs(robot(RID),putdown,t).
ab(on(PRID,SID,AMT),t)		:-	holds(on(PRID,SID,AMT),t-1),
                                holds(carries(RID,SID),t-1),
                                occurs(object(robot, RID), action(deliver, (RQID, PRID, RQAMT)), t).
ab(request(RQID,PRID,PID,RQAMT),t) :-	holds(request(RQID,PRID,PID,RQAMT),t-1), occurs(object(robot, RID), action(deliver, (RQID, PRID, AMT)), t).
ab(request(RQID,PRID,PID,RQAMT),t) :-	holds(done(RQID,PRID,PID,RQAMT),t).
ab(done(RQID,PRID,PID,RQAMT),t)    :-	holds(done(RQID,PRID,PID,RQAMT),t-1).

%--------------------------------------------------%

%%	STATIC LAWS
%       There can only be one robot and one shelf at a node at the same time.
:-	node(X,Y), 2{holds(at(robot(RID),node(X,Y)),t): robot(RID)}.
:-	node(X,Y), 2{holds(at(shelf(SID),node(X,Y)),t): shelf(SID)}.

%       A robot/shelf can only be at one node at a time.
:-	robot(RID), 2{holds(at(robot(RID),node(X,Y)),t) : node(X,Y)}.
:-	shelf(SID), 2{holds(at(shelf(SID),node(X,Y)),t) : node(X,Y)}.

%       Two robots can't swap places as they would crash.
:-	holds(at(robot(RID1),node(X1,Y1)),t), holds(at(robot(RID2),node(X2,Y2)),t),
	holds(at(robot(RID1),node(X2,Y2)),t-1), holds(at(robot(RID2),node(X1,Y1)),t-1),
	RID1<RID2, |X2-X1|+|Y2-Y1|==1.

%       On higway nodes shelfs can't be putdown and robots can't do nothing for more than one time step.
:-  highway(X,Y), not node(X,Y).
:-  highway(X,Y), holds(at(robot(RID),node(X,Y)),t), occurs(robot(RID),putdown,t).
:-  highway(X,Y), holds(at(robot(RID),node(X,Y)),t), not moved(robot(RID),t-1), not moved(robot(RID),t), not init(at(robot(RID),node(X,Y))).

%       Small scope loop preventions preventing opposite actions at adjacent time points.
:- occurs(robot(RID),move(DX,DY),t), occurs(robot(RID),move(-DX,-DY),t-1).
:- occurs(robot(RID),pickup,t), occurs(robot(RID),putdown,t-1).
:- occurs(robot(RID),putdown,t), occurs(robot(RID),pickup,t-1).
	
%--------------------------------------------------%
#program check(t).
#external query(t).
%%	GOAL - CONDITION
%       The goal is reached when there are no more requests.
goal(t) :- not holds(request(_,_,_,_),t).
:- not goal(t), query(t).
%       The optimization is set to find the plan with the least amount of actions.
%#minimize{ 1, RID, T : occurs(robot(RID),_,T)}.

%--------------------------------------------------%

#show occurs/3.
#show init/2.
