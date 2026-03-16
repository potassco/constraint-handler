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

_computedIdx(E,val(bool,true)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, val(T, V)),
    _computeIdx(E, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx(E,val(bool,false)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, val(T, V)),
    not _computeIdx(E, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx(E,val(bool,false)) :- _computeIdx(E, eq),
    _computeIdx(E, 1, val(T, V)),
    not _computeIdx(E, 0, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx(E,val(bool,true)) :- _computeIdx(E, neq),
    _computeIdx(E, 0, val(T, V)),
    not _computeIdx(E, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx(E,val(bool,true)) :- _computeIdx(E, neq),
    _computeIdx(E, 1, val(T, V)),
    not _computeIdx(E, 0, val(T, V)),
    representation(T, extensional), T != none, T != float.

_computedIdx(E,val(bool,false)) :- _computeIdx(E, neq),
    _computeIdx(E, 0, val(T, V)),
    _computeIdx(E, 1, val(T, V)),
    representation(T, extensional), T != none, T != float.
