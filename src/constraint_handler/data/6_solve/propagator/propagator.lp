propagator_variable_declare(X,fromFacts,LBL) :- _passed(propagator,LBL,variable_declare(X,fromFacts)).
propagator_variable_declare(X,open,LBL) :- _passed(propagator,LBL,variable_declare(X,open)).

%_bool_evaluate(C,LBL) :- _passed(propagator,LBL,variable_domain(X,D,C)).
%1 {propagator_variable_domain(X,D,LBL) : _passed(propagator,LBL,variable_domain(X,D,C)), _bool_evaluated(C,val(bool,true)) } 1 :- _passed(propagator,LBL,variable_declare(X,fromFacts)).
1 {propagator_variable_domain(X,D,LBL) : _passed(propagator,LBL,variable_domain(X,D,C)) } 1 :- _passed(propagator,LBL,variable_declare(X,fromFacts)).

#script (python)

from clingo import Number

order_num = {}
def order(X,E):
    if X not in order_num:
        order_num[X] = {}
    if E not in order_num[X]:
        order_num[X][E] = Number(len(order_num[X].keys()))

    return order_num[X][E]
#end.

order(CNAME,X,E,IDX) :- _passed(propagator,CNAME,variable_domain(X,E,C)), IDX = @order((propagator,X),E).

active(CNAME,X,IDX-1) :- order(CNAME,X,E,IDX), propagator_variable_domain(X,E,CNAME), IDX > 0.
active(CNAME,X,N-1) :- active(CNAME,X,N), N > 0.

_propagator_ensure(operation(neq,(variable(X),(E,()))),CNAME) :- _passed(propagator,CNAME,variable_domain(X,E,C)), active(CNAME,X,IDX), order(CNAME,X,E,IDX).

_bool_evaluate(E,LBL) :- _propagator_ensure(E,LBL).
:- _propagator_ensure(E,LBL), not _bool_evaluated(E,val(bool,true)), not _bool_evaluated(E,bad).

propagator_variable_define(X,E,CNAME) :- _passed(propagator,CNAME,variable_assign(X,E)).
%_passed(propagator,CNAME,variable_domain(X,E,val(bool,true))) :- _passed(propagator,CNAME,variable_choice(X,E)).
%propagator_variable_assign(X,E,CNAME) :- _passed(propagator,CNAME,variable_assign(X,E)).
%propagator_variable_choice(X,E,CNAME) :- _passed(propagator,CNAME,variable_choice(X,E)).
%propagator_variable_default(X,E,C,P,CNAME) :- _passed(propagator,CNAME,variable_default(X,E,C,P)). %% TODO: temporary hack
propagator_variable_define(X,E,CNAME) :- _passed(propagator,CNAME,variable_define(X,E,val(bool,true))).
_bool_evaluate(C,CNAME) :- _passed(propagator,CNAME,variable_define(X,E,C)), C != val(bool,true), C != val(bool,false).
propagator_variable_define(X,E,CNAME) :- _passed(propagator,CNAME,variable_define(X,E,C)), _bool_evaluated(C,val(bool,true)).

propagator_set_declare(X,CNAME) :- _passed(propagator,CNAME,variable_declare(X,set)).
propagator_set_assign(X,E,C,LBL) :- _passed(propagator,LBL,set_assign(X,E,C)).

propagator_multimap_assign(X,K,V,LBL) :- _passed(propagator,LBL,multimap_assign(X,K,V)).
propagator_multimap_declare(X,LBL) :- _passed(propagator,LBL,variable_declare(X,multimap)).

propagator_share_value(E,LBL) :- _passed(propagator,LBL,share_value(E)).

propagator_warning_forbid(KIND,LBL) :- _warning_forbid(KIND,LBL).
propagator_warning_ignore(KIND,LBL) :- _warning_ignore(KIND,LBL).
