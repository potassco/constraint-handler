%%% bools(e) = {] bools(t) = { true } bools(f) = { false} bools(b) = { true, false }

set_declare(d_bools,bools(e;t;f;b)).
set_assign(a_bools,bools(t),val(bool,true)).
set_assign(a_bools,bools(f),val(bool,false)).
set_assign(a_bools,bools(b),val(bool,(true;false))).

evaluate(set_fold,(val(function,conj),(variable(bools(e;t;f;b)),(val(bool,true),())))).
evaluate(set_fold,(val(function,disj),(variable(bools(e;t;f;b)),(val(bool,false),())))).
