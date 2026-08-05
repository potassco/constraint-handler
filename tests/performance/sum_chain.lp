#const input_w1 = 2.
#const input_w2 = 1.
#const middle_offset = 25.
#const tail_offset = 1.

execution_declare(
    dummy,
    snippet,
    seq2(
        assign(t2, operation(add, (variable(w1), (variable(w2), ())))),
        seq2(
            assign(t3, operation(add, (variable(t2), (val(int, middle_offset), ())))),
            seq2(
                assign(t4, operation(add, (variable(t3), (val(int, tail_offset), ())))),
                assign(t5, operation(add, (variable(t4), (val(int, 0), ()))))
            )
        )
    ),
    (w1, (w2, ())),
    (t5, ())
).
execution_run(dummy, snippet).
variable_define(execution_input(snippet, w1), val(int, input_w1)).
variable_define(execution_input(snippet, w2), val(int, input_w2)).
