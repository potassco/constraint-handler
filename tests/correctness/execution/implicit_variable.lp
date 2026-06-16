variable_define(execution_input(miss_input,v1),val(int,2)).
execution_declare(miss_input,
    seq2(assign(v2,variable(v1)),
    seq2(assign(v3,variable(v4)),
    noop)),
    (v1,(v2,())),
    (v1,(v2,(v3,(v5,()))))).
execution_run(miss_input).
