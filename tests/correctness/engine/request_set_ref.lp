variable_declare(odd0,set,odd0).
set_assign(odd0,val(int,1),val(bool,true),odd0).
set_assign(odd0,val(int,3),val(bool,true),odd0).

variable_declare(sma0,set,sma0).
set_assign(sma0,val(int,1),val(bool,true),sma0).
set_assign(sma0,val(int,2),val(bool,true),sma0).

variable_define(odd1,variable(odd0),val(bool,true),odd1).
variable_define(odd2,variable(odd1),val(bool,true),odd2).

variable_define(sma1,variable(sma0),val(bool,true),sma1).
variable_define(sma2,variable(sma1),val(bool,true),sma2).

variable_define(cup2,operation(union,(variable(odd2),(variable(sma2),()))),val(bool,true),cup2).
variable_define(cap1,operation(inter,(variable(odd1),(variable(sma1),()))),val(bool,true),cap1).
variable_define(cap2,variable(cap1),val(bool,true),cap2).

variable_define(curd2,operation(length,(variable(cup2),())),val(bool,true),curd2).
variable_define(card2,operation(length,(variable(cap2),())),val(bool,true),card2).

% engine_request(ground,sma0).
engine_request(compile,odd0).
engine_request(propagator,cap2).
engine_request(propagator,curd2).
engine_request(propagator,card2).
