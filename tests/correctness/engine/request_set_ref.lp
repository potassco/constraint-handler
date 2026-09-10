variable_declare(odd0,set,odd0).
set_assign(odd0,val(int,1),odd0).
set_assign(odd0,val(int,3),odd0).

variable_declare(sma0,set,sma0).
set_assign(sma0,val(int,1),sma0).
set_assign(sma0,val(int,2),sma0).

variable_define(odd1,variable(odd0),odd1).
variable_define(odd2,variable(odd1),odd2).

variable_define(sma1,variable(sma0),sma1).
variable_define(sma2,variable(sma1),sma2).

variable_define(cup2,operation(union,(variable(odd2),(variable(sma2),()))),cup2).
variable_define(cap1,operation(inter,(variable(odd1),(variable(sma1),()))),cap1).
variable_define(cap2,variable(cap1),cap2).

variable_define(curd2,operation(length,(variable(cup2),())),curd2).
variable_define(card2,operation(length,(variable(cap2),())),card2).

% engine_request(sma0, ground).
engine_request(odd0, compile).
engine_request(cap2, propagator).
engine_request(curd2, propagator).
engine_request(card2, propagator).
