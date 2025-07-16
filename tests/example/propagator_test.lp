#include "includeAll.lp".


%%% p_e1: e1 = guess true or false
%%% p_e2: e2 = guess true or false
%%% p_ec: ec = e1 & e2
%%% p_ed: ed = e1 | e2
%%% p_ee: ensure ec <-> ed

%%% there should be 2 models: { e1=true, e2=true } and { e1=false, e2=false }

1 { assign(p_e1,e1,val(bool,(true;false))) } 1.
#heuristic assign(p_e1,e1,val(bool,(false))). [5,level]
#heuristic assign(p_e1,e1,val(bool,(false))). [1,sign]

% assign(p_e1,e1,val(bool,(true))).

% 1 { assign(p_e2,e2,val(bool,(true;false))) } 1.
assign(p_e2,e2,val(bool,(true))).
assign(p_ec,ec,operation(conj,(variable(e1),(variable(e2),())))).
assign(p_ed,ed,operation(disj,(variable(e1),(variable(e2),())))).
ensure(p_ee,operation(leqv,(variable(ec),(variable(ed),())))).

%%% this refers to the new propagator engine.
%%% Because the propagator is not implemented yet, we obtain 4 models when the next line is included.
requestEngine((p_e1;p_e2;p_ec;p_ed;p_ee),propagator).

%%% This refers to the default engine.
%%% If the next line is included instead of the above, then there will be 2 models, as intended.
%requestEngine((p_e1;p_e2;p_ec;p_ed;p_ee),compile).



#show value/3.
#show assign/3.
#script (python)

import clingo
import constraint_handler.propagator as prop

def main(prg):

    propagator = prop.ConstraintHandlerPropagator()
    prg.register_propagator(propagator)
    prg.ground()
    prg.solve()

#end.
