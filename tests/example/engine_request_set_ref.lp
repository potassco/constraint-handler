set_declare(odd0,odd0).
set_assign(odd0,odd0,val(int,1)).
set_assign(odd0,odd0,val(int,3)).

set_declare(sma0,sma0).
set_assign(sma0,sma0,val(int,1)).
set_assign(sma0,sma0,val(int,2)).

variable_define(odd1,odd1,variable(odd0)).
variable_define(odd2,odd2,variable(odd1)).

variable_define(sma1,sma1,variable(sma0)).
variable_define(sma2,sma2,variable(sma1)).

variable_define(cup2,cup2,operation(union,(variable(odd2),(variable(sma2),())))).
variable_define(cap1,cap1,operation(inter,(variable(odd1),(variable(sma1),())))).
variable_define(cap2,cap2,variable(cap1)).

variable_define(curd2,curd2,operation(length,(variable(cup2),()))).
variable_define(card2,card2,operation(length,(variable(cap2),()))).

% requestEngine(sma0, ground).
requestEngine(odd0, compile).
requestEngine(cap2, propagator).
requestEngine(curd2, propagator).
requestEngine(card2, propagator).
