%%%%%%%%%%%%%%%%% add mult
operator_declare_variadic(OP,T,T,1) :- T = int, OP = (add;mult).

% Direct (compile-engine) computation for addition.
% This avoids constructing the fully-evaluated argument tuple and instead
% aggregates over per-argument values derived by direct.lp via _computeIdx/3.
_computedIdx(E, val(int, N)) :- _computeIdx(E, add), E = operation(add, ARGS), not _direct_doCompute(add, ARGS),
    N = #sum { V, IDX : _computeIdx(E, IDX, val(int, V)) }.

% Value-tuple computation for addition.
% Used by encodings that explicitly create `_compute(add,ARGS)` with ARGS being
% a tuple of `val(int,_)` terms (e.g. set_fold).
_computed(add, ARGS, val(int, N)) :- _compute(add, ARGS),
    0 = #sum { 1, IDX : (IDX, _) = @pythonEnumerateElements(ARGS);
              -1, IDX : (IDX, val(int, _)) = @pythonEnumerateElements(ARGS) },
    N = #sum { V, IDX : (IDX, val(int, V)) = @pythonEnumerateElements(ARGS) }.


_computed(OP, ARGS, val(int, 1)) :- _compute(OP, ARGS), OP=mult, ARGS = ().
_compute(OP, TAIL) :- _compute(OP, ARGS), OP=mult, ARGS = (val(int, _), TAIL).
_computed(OP, ARGS, val(int, V1 * VTAIL)) :-
    _compute(OP, ARGS),
    OP=mult,
    ARGS = (val(int, V1), TAIL),
    _computed(OP, TAIL, val(int, VTAIL)).

%%%%%%%%%%%%%%%%% sub int_div pow
operator_declare(OP,(T,(T,())),T) :- T = int, OP = (sub;pow).
operator_declare(OP,(T1,(T2,())),T) :- T = int, T1 = (int;float), T2 = (int;float), OP = int_div.
_computed(OP,ARGS,val(int,V1-V2))  :- _compute(OP,ARGS), OP=sub,  ARGS = (val(int,V1),(val(int,V2),())).
_computed(OP,ARGS,val(int,V1/V2))  :- _compute(OP,ARGS), OP=int_div,  ARGS = (val(int,V1),(val(int,V2),())), V2!=0.
_computed(OP,ARGS,bad) :- _compute(OP,ARGS), OP=(int_div;float_div),  ARGS = (val(int,V1),(val(int,V2),())), V2=0.
warning(expression(zeroDivisionError),(),(OP,ARGS))  :- _compute(OP,ARGS), OP=(int_div;float_div),  ARGS = (val(int,V1),(val(int,V2),())), V2=0.
_computed(OP,ARGS,val(int,V1**V2)) :- _compute(OP,ARGS), OP=pow,  ARGS = (val(int,V1),(val(int,V2),())).

%%%%%%%%%%%%%%%%% abs minus
operator_declare(OP,(T,()),T) :- T = int, OP = (abs;minus).
_computed(OP,ARGS,val(int,|V|)) :- _compute(OP,ARGS), OP=abs,   ARGS = (val(int,V),()).
_computed(OP,ARGS,val(int,-V))  :- _compute(OP,ARGS), OP=minus, ARGS = (val(int,V),()).

%%%%%%%%%%%%%%%%% comparison equality
operator_declare(OP,(T,(T,())),bool) :- T = int, OP = (eq;neq;leq;lt;geq;gt).

% Direct (compile-engine) computation for binary integer equality.
% This avoids building the fully-evaluated argument tuple (and thus avoids
% Cartesian-product grounding) by iterating over values of the first argument
% and checking for a matching value in the second argument.
%COULD BE CORRECT, but type inference is not ready yet
_computedIdx(E, val(bool,true)) :- _direct_eq_int_int_binary(E, eq, ARGS),
    E = operation(eq, (A, (B, ()))),
    _computeIdx(E, 0, val(int, V1)),
    _computeIdx(E, 1, val(int, V1)).
_computedIdx(E, val(bool,false)) :- _direct_eq_int_int_binary(E, eq, ARGS),
    E = operation(eq, (A, (B, ()))),
    _computeIdx(E, 0, val(int, V1)),
    not _computeIdx(E, 1, val(int, V1)).

_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=leq, ARGS = (val(int,V1),(val(int,V2),())), V1 <= V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=lt,  ARGS = (val(int,V1),(val(int,V2),())), V1 <  V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=geq, ARGS = (val(int,V1),(val(int,V2),())), V1 >= V2.
_computed(OP,ARGS,val(bool,true))  :- _compute(OP,ARGS), OP=gt,  ARGS = (val(int,V1),(val(int,V2),())), V1 >  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=eq,  ARGS = (val(int,V1),(val(int,V2),())), V1 != V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=neq, ARGS = (val(int,V1),(val(int,V2),())), V1 =  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=leq, ARGS = (val(int,V1),(val(int,V2),())), V1 >  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=lt,  ARGS = (val(int,V1),(val(int,V2),())), V1 >= V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=geq, ARGS = (val(int,V1),(val(int,V2),())), V1 <  V2.
_computed(OP,ARGS,val(bool,false)) :- _compute(OP,ARGS), OP=gt,  ARGS = (val(int,V1),(val(int,V2),())), V1 <= V2.

_computed(OP,ARGS,RES) :- _compute(OP,ARGS), OP=float_div, ARGS = (val(int,_),(val(int,V2),())), V2!=0,
  RES = @pythonEvalExpr(operation(OP,ARGS),(),ID),
  _main_solverIdentifier(ID).
