multimap_declare(test, my_multimap).
multimap_assign(test, my_multimap, val(symbol,some_key),val(int,(1;2;3))).

execution_declare(test, exec_internal, STMT, (), (internal_out,())) :-
    STMT = assign(internal_out, operation(multimap_make, ((val(symbol,some_key),val(int,1)),((val(symbol,some_key),val(int,2)),())))).

execution_declare(test, exec_internal_empty, STMT, (), (internal_out,())) :-
    STMT = assign(internal_out, operation(multimap_make, ())).

variable_define(test, execution_input(exec_external, my_multimap), variable(my_multimap)).
execution_declare(test, exec_external, STMT, (my_multimap,()), (external_out,())) :-
    STMT = assign(external_out, variable(my_multimap)).

execution_run(test, exec_external).
execution_run(test, exec_internal).
execution_run(test, exec_internal_empty).

evaluate(isin, (val(symbol,some_key),(variable(execution_output(exec_internal,internal_out)),()))).
evaluate(isin, (val(symbol,some_key),(variable(execution_output(exec_external,external_out)),()))).
evaluate(isin, (val(symbol,some_key),(variable(execution_output(exec_internal_empty,internal_out)),()))).
