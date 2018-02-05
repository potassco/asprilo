% = CHECKER ENCODINGS FOR THE DEFAULT PROBLEM DOMAIN ===========================

% - Initial Setup --------------------------------------------------------------
%
%   Sets up inital state, horizon and general inertia axiom

#include "../default/init.lp".


% - Checks and Book-Keeping Entailments Per Action -----------------------------
%
%   Per each action, conduct
%   - checks for preconditions
%   - "book-keeping" entailments for effects and related inertial abnormalities

#include "../default/action-move.lp".
#include "../default/action-pickup.lp".
#include "../default/action-putdown.lp".
#include "action-deliver.lp".


% - Checks for Static Law Violations -------------------------------------------

#include "../default/static.lp".


% - Goal condition -------------------------------------------------------------
%
%   Define:
%   1. the necessary sequence of actions and preconditions to fulfill an oder; and
%   2. the general goal that all orders are fulfilled (ie., fully processed)

% Order fulfillment
#include "fulfillment.lp".

% General goal
#include "../default/goal.lp".
