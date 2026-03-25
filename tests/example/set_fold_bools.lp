%%% bools(e) = {] bools(t) = { true } bools(f) = { false} bools(b) = { true, false }

set_declare(bools(e;t;f;b)).
set_assign(bools(t),val(bool,true)).
set_assign(bools(f),val(bool,false)).
set_assign(bools(b),val(bool,(true;false))).

evaluate(set_fold,(val(function,conj),(variable(bools(e;t;f;b)),(val(bool,true),())))).
evaluate(set_fold,(val(function,disj),(variable(bools(e;t;f;b)),(val(bool,false),())))).
