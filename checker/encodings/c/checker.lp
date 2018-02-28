% = CHECKER ENCODINGS FOR THE C PROBLEM DOMAIN ===========================

% - Initial Setup --------------------------------------------------------------
%
%   Sets up inital state, horizon and general inertia axiom

#include "../a/init.lp".


% - Checks and Book-Keeping Entailments Per Action -----------------------------
%
%   Per each action, conduct
%   - checks for preconditions
%   - "book-keeping" entailments for effects and related inertial abnormalities

#include "../a/action-move.lp".
#include "../a/action-pickup.lp".
#include "../a/action-putdown.lp".
% Note that for domain c, delivery actions are implicit!

% - Checks for Static Law Violations -------------------------------------------

#include "../a/static.lp".


% - Goal condition -------------------------------------------------------------
%
%   Define:
%   1. the necessary sequence of actions and preconditions to fulfill an oder; and
%   2. the general goal that all orders are fulfilled (ie., fully processed)

% Order fulfillment
#include "fulfillment.lp".

% General goal
#include "../a/goal.lp".
