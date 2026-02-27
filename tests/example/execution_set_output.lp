% Regression test: execution outputs must work for intensional reference values
% (e.g., sets are represented as ref(set, ...)).
execution_declare(dummy, my_exec, STMT, (), (x,())) :-
    STMT = assign(x, operation(set_make, (val(int,1),()))).

execution_run(dummy, my_exec).
