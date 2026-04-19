execution_declare(test,
    statement_python("y = x + 1"),
    ("x",()),
    ("y",())).

variable_declare(execution_input(test,"x"),fromFacts).
variable_domain(execution_input(test,"x"),val(int,2)).

execution_run(test).

#show value/2.
#show warning/3.