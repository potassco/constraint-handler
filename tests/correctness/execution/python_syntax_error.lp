%execution_declare(example,statement_python("1 ++"),(),(),val(bool,true)).
%
%{ dontforbid }.
%warning_forbid(expression(pythonError)) :- not dontforbid.

execution_declare(example,statement_python("1 ++"),(),(),variable(df)).
dontforbid :- bool_evaluated(variable(df),val(bool,true)).
%{ dontforbid }.
variable_declare(df,boolDomain).
bool_evaluate(variable(df)).
%warning_forbid(expression(pythonError)).