set_declare(my_set).
set_assign(my_set, val(int,(1;2;3))).

execution_declare(exec_internal, STMT, (), (internal_out,())) :-
    STMT = assign(internal_out, operation(set_make, (val(int,1),(val(int,2),())))).

execution_declare(exec_internal_empty, STMT, (), (internal_out,())) :-
    STMT = assign(internal_out, operation(set_make, ())).

variable_define(execution_input(exec_external, my_set), variable(my_set)).
execution_declare(exec_external, STMT, (my_set,()), (external_out,())) :-
    STMT = assign(external_out, variable(my_set)).

execution_run(exec_external).
execution_run(exec_internal).
execution_run(exec_internal_empty).

evaluate(set_isin, (val(int,2),(variable(execution_output(exec_internal,internal_out)),()))).
evaluate(set_isin, (val(int,2),(variable(execution_output(exec_external,external_out)),()))).
evaluate(set_isin, (val(int,2),(variable(execution_output(exec_internal_empty,internal_out)),()))).
