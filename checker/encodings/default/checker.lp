% = CHECKER ENCODINGS FOR THE DEFAULT PROBLEM DOMAIN ===========================

% - Initial Setup --------------------------------------------------------------
%
%   Sets up inital state, horizon and general inertia axiom

#include "init.lp".


% - Checks and Book-Keeping Entailments Per Action -----------------------------
%
%   Per each action, conduct
%   - checks for preconditions
%   - "book-keeping" entailments for effects and related inertial abnormalities

#include "action-move.lp".
#include "action-pickup.lp".
#include "action-putdown.lp".
#include "action-deliver.lp".


% - Checks for Static Law Violations -------------------------------------------

#include "static.lp".

% - Goal condition -------------------------------------------------------------

#include "goal.lp".
