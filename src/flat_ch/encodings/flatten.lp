%
% This module contains the flattening encoding, which transforms high-level input predicates into a normalized,
% flat representation that is easier to process in subsequent stages of the solving pipeline.
%
% It represents the - ONLY - encoding that should operate on `_fch_input` predicates. All other encodings should 
% only operate on the flattened predicates defined here.
%
% In the future, I hope to add optimizations here to simplify expressions where possible, and to perform some 
% basic static analysis to catch errors early on.

% All input declarations have to be flattened.
_fch_flat(FLAT)                          :- _fch_input(TERM), FLAT = @fch_flatten(TERM).
_fch_flat(SSA)                           :- _fch_ssa(TERM), SSA = @fch_ssa(TERM).
