%%% raises warning undeclared but does not appear in the answer set
set_assign(b,val(string,"good bye")).

warning_ignore(variable(undeclared)).
