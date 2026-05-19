%% a = false or nothing
%% b = true or nothing

%%% any:
%%% snot a == true   snot a == false
%%% wnot b == true   wnot b == false

%%% all:
%%% snot b == false
%%% not (snot b) == true
%%% wnot a == true

variable_declare(a,fromFacts).
variable_domain(a,(val(bool,false); val(none,none))).
variable_declare(b,fromFacts).
variable_domain(b,(val(bool,true); val(none,none))).

evaluate(snot,(variable(a),())).
evaluate(snot,(variable(b),())).
evaluate(lnot,(operation(snot,(variable(b),())),())).
evaluate(wnot,(variable(a),())).
evaluate(wnot,(variable(b),())).