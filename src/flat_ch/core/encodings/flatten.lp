%
% This module contains the flattening encoding, which transforms high-level input predicates into a normalized,
% flat representation that is easier to process in subsequent stages of the solving pipeline.
%
% It represents the - ONLY - encoding that should operate on `_fch_input` predicates. All other encodings should
% only operate on the flattened predicates defined here.
%
% In the future, I hope to add optimizations here to simplify expressions where possible, and to perform some
% basic static analysis to catch errors early on.

% All input declarations are first registered into a shared Python-side IR.
_fch_registered(TERM, ID) :- _fch_input(TERM), ID = @fch_register(TERM).
registered :- _fch_registered(_, _).
_fch_flat(FLAT) :- registered, FLAT = @fch_flatten().
