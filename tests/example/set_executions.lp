set_declare(test, my_set).
set_assign(test, my_set, val(int,(1;2;3))).

execution_declare(test, exec_internal, STMT, (), (internal_out,())) :-
    STMT = assign(internal_out, operation(set_make, (val(int,1),(val(int,2),())))).

execution_declare(test, exec_internal_empty, STMT, (), (internal_out,())) :-
    STMT = assign(internal_out, operation(set_make, ())).

variable_define(test, execution_input(exec_external, my_set), variable(my_set)).
execution_declare(test, exec_external, STMT, (my_set,()), (external_out,())) :-
    STMT = assign(external_out, variable(my_set)).

execution_run(test, exec_external).
execution_run(test, exec_internal).
execution_run(test, exec_internal_empty).

evaluate(isin, (val(int,2),(variable(execution_output(exec_internal,internal_out)),()))).
evaluate(isin, (val(int,2),(variable(execution_output(exec_external,external_out)),()))).
evaluate(isin, (val(int,2),(variable(execution_output(exec_internal_empty,internal_out)),()))).
