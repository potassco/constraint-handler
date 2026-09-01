%%%% Instance
variable_declare(x,fromFacts).
variable_domain(x,val(int,1..10)).

variable_declare(y,fromFacts).
variable_domain(y,val(int,1..10)).

ensure(operation(leq,(operation(add,(variable(x),(variable(y),()))),(val(int,5),())))). % x + y <= 5


%%%% For testing
%%% y = 3
bool_evaluate(operation(eq,(variable(y),(val(int,3),())))).

%%% x <= 4
bool_evaluate(operation(leq,(variable(x),(val(int,4),())))).

%%% x*y <= 8
bool_evaluate(operation(leq,(operation(mult,(variable(x),(variable(y),()))),(val(int,8),())))).

%%% x<=2 or y<=2
bool_evaluate(operation(disj,(operation(leq,(variable(x),(val(int,2),()))),(operation(leq,(variable(y),(val(int,2),()))),())))).

%%% x<=4 and y<=4
bool_evaluate(operation(conj,(operation(leq,(variable(x),(val(int,4),()))),(operation(leq,(variable(y),(val(int,4),()))),())))).

%%% x>=3 and y>=3
bool_evaluate(operation(conj,(operation(geq,(variable(x),(val(int,3),()))),(operation(geq,(variable(y),(val(int,3),()))),())))).

%%% x<=2 and y<=2
bool_evaluate(operation(conj,(operation(leq,(variable(x),(val(int,2),()))),(operation(leq,(variable(y),(val(int,2),()))),())))).