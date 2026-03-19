%%%%%%%%%%%%%%%%% generic eq/neq for extensional base types
% Implements equality/inequality in a linear (non-Cartesian) way:
% - eq true  iff there is a common value
% - eq false iff one side has a value not present on the other
% - neq is the dual (swap true/false)
%
% Excludes:
% - `none`: conditionals.lp defines the intended semantics
% - `float`: float.lp defines numeric equality (e.g., float("2") == float("2.0"))
%
operator_declare(OP,(T,(T,())),bool) :- representation(T,extensional), T != none, T != float, OP = (eq;neq).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(T, V)),
    _computeIdx_id(E_ID, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(T, V)),
    not _computeIdx_id(E_ID, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 1, val(T, V)),
    not _computeIdx_id(E_ID, 0, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, neq),
    _computeIdx_id(E_ID, 0, val(T, V)),
    not _computeIdx_id(E_ID, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, neq),
    _computeIdx_id(E_ID, 1, val(T, V)),
    not _computeIdx_id(E_ID, 0, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, neq),
    _computeIdx_id(E_ID, 0, val(T, V)),
    _computeIdx_id(E_ID, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.
