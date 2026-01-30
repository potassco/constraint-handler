variable_declare(bla,numeric(int),fromFacts).
variable_domain(numeric(int),val(int,1..3)).
variable_declare(bla,numeric(float),fromFacts).
variable_domain(numeric(float),val(float,float(1..3))).
variable_declare(bla,boolean,boolDomain).

variable_define(bla,yep(O,X1,X2),EXPR) :-
  X1=(numeric(int;float)),
  X2=(numeric(int;float)),
  O=(add;mult),
  EXPR=operation(O,(variable(X1),(variable(X2),()))).

variable_define(bla,nah(O,X1,X2),EXPR) :-
  X1=(boolean),
  X2=(numeric(int;float);boolean),
  O=(add;mult),
  EXPR=operation(O,(variable(X1),(variable(X2),()))).

% the tests would pass with these declarations included, but they don't belong here.
%operator_declare(add,(float,(float,())),float).
%operator_declare(add,(float,(int,())),float).
%operator_declare(add,(int,(float,())),float).
%operator_declare(mult,(float,(float,())),float).
%operator_declare(mult,(float,(int,())),float).
%operator_declare(mult,(int,(float,())),float).
