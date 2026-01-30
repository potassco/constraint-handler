%%% raise warning(variable(undeclared),...)
variable_define(d_0,v0,val(int,2)).
variable_define(d_1,execution_input(stmt,v1),variable(v0)).
variable_define(d_2,v2,variable(b)).
variable_define(d_3,execution_input(stmt,v3),variable(v20)).
execution_declare(d_4,stmt,
    seq2(assign(v4,variable(v21)),
    seq2(assign(v6,variable(v1)),
    seq2(assign(vd,variable(v5)),
         assign(v5,variable(v4))))),
    (v0,(v1,(v2,(v3,())))),
    (v4,(v7,(v8,())))).
variable_define(d_5,v9,variable(execution_output(stmt,v4))).
variable_define(d_6,va,variable(v7)).
variable_define(d_7,vb,variable(execution_input(stmt,v8))).
variable_define(d_3,execution_output(stmt,vc),val(int,3)).

%% something_something_for_vc
%% not_warning(variable(undeclared),(),v1)
