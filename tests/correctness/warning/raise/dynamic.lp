variable_declare(flag,boolDomain).
warning_raise(positive,variable(flag),notice).
warning_raise(negative,operation(lnot,(variable(flag),())),notice).
warning_raise(shared,variable(flag),positive).
warning_raise(shared,operation(lnot,(variable(flag),())),negative).
