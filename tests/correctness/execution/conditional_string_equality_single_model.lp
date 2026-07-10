% Benchmark-like pattern:
% 1. derive an intermediate bool __condition_holds__ from a string equality
% 2. initialize result with false
% 3. overwrite result with true when __condition_holds__ is true
% 4. compare generated bool outputs within the same model via evaluated/3

execution_declare(flagger, STMT, (mode, ()), ("__condition_holds__", ("result", ("other", ())))) :-
    MODE_A = operation(eq, (variable(mode), (val(string, "a"), ()))),
    MODE_B = operation(eq, (variable(mode), (val(string, "b"), ()))),
    STMT = seq2(
        assign("__condition_holds__", MODE_A),
        seq2(
            assign("result", val(bool, false)),
            seq2(
                if(variable("__condition_holds__"), assign("result", val(bool, true)), noop),
                assign("other", MODE_B)
            )
        )
    ).

variable_declare(execution_input(flagger, mode), fromFacts).
variable_domain(execution_input(flagger, mode), val(string, ("a"; "b"))).

execution_run(flagger).

evaluate(
    leqv,
    (
        variable(execution_output(flagger, "__condition_holds__")),
        (operation(eq, (variable(execution_input(flagger, mode)), (val(string, "a"), ()))), ())
    )
).
evaluate(
    leqv,
    (
        variable(execution_output(flagger, "result")),
        (variable(execution_output(flagger, "__condition_holds__")), ())
    )
).
evaluate(
    lxor,
    (
        variable(execution_output(flagger, "result")),
        (variable(execution_output(flagger, "other")), ())
    )
).

#show value/2.
#show evaluated/3.