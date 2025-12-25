#include "includeAll.lp".


%%% p_e1: e1 = guess true or false
%%% p_e2: e2 = guess true or false
%%% p_ec: ec = e1 & e2
%%% p_ed: ed = e1 | e2
%%% p_ee: ensure ec <-> ed

%%% there should be 2 models: { e1=true, e2=true } and { e1=false, e2=false }

% variable_declare(p_e1,e1,boolDomain).

% variable_define(p_e1,e1,val(bool,(true))).

% variable_declare(p_e2,e2,boolDomain).
%variable_define(p_e2,e2,val(bool,(true))).
%variable_define(p_ec,ec,operation(conj,(variable(e1),(variable(e2),())))).
%variable_define(p_ed,ed,operation(disj,(variable(e1),(variable(e2),())))).
%ensure(p_ee,operation(leqv,(variable(ec),(variable(ed),())))).
%ensure(p_ee,variable(ec)).


variable_declare(p_x,x,fromFacts).
variable_domain(x,val(int,1..2)).
variable_declare(p_y,y,fromFacts).
variable_domain(y,val(int,1..2)).
variable_declare(p_z,z,fromFacts).
variable_domain(z,(PROD;SUM)) :-
    PROD = operation(mult,(variable(x),(variable(y),()))),
    SUM = operation(add,(variable(x),(variable(y),()))).

1 { ensure(p_zs,operation(disj,(ZSMALL,(ZBIG,())))) } :-
   ZSMALL = operation(leq,(variable(z),(val(int,3),()))),
   ZBIG = operation(geq,(variable(z),(val(int,4),()))).

%%% this refers to the new propagator engine.
%%% Because the propagator is not implemented yet, we obtain 4 models when the next line is included.
%requestEngine((p_e1;p_e2;p_ec;p_ed;p_ee),propagator).

requestEngine((p_x;p_y;p_z;p_zs),propagator).

%%% This refers to the default engine.
%%% If the next line is included instead of the above, then there will be 2 models, as intended.
%requestEngine((p_e1;p_e2;p_ec;p_ed;p_ee),compile).



#show value/3.
% #show assign/3.
