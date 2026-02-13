#show warning/3.
#show value/2.

%%% 3 equivalent ways to assign x/y to z and reject models where z is <= 1.5


%%% version 1
%%% using fact format
execution_declare(dummy,myprog(1),seq2(assign("z",operation(fdiv,(variable("x"),(variable("y"),())))),assert(operation(lt,(val(float,float("1.5")),(variable("z"),()))))),("x",("y",())),()) :- active_version(1).

%%% version 2
%%% using solver_environment.constrain
%%% z = x/y
%%% solver_environment.constrain(1.5 < z)
%%%
execution_declare(dummy,myprog(2),statement_python("z = x/y\nsolver_environment.constrain(1.5 < z)"),("x",("y",())),()) :- active_version(2).

%%% version 3
%%% using solver_environment.FailIntegrityExn
%%% z = x/y
%%% if 1.5 <= z:
%%%     raise solver_environment.FailIntegrityExn
%%%
execution_declare(dummy,myprog(3),statement_python("z = x/y\nif z <= 1.5:\n  raise solver_environment.FailIntegrityExn"),("x",("y",())),()) :- active_version(3).

1 { active_version(1..3) } 1.
variable_declare(dummy,execution_input(myprog(P),("x";"y")),fromFacts) :- active_version(P).
variable_domain(execution_input(myprog(P),"x"),val(int,2)) :- active_version(P).
variable_domain(execution_input(myprog(P),"y"),val(int,0..2)) :- active_version(P).
execution_run(dummy,myprog(P)) :- active_version(P).

ignore_warning(type(failed_operation)).