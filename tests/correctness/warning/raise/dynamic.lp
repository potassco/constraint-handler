variable_declare(flag,boolDomain).
warning_raise(positive,positive_message,variable(flag),notice).
warning_raise(negative,negative_message,operation(lnot,(variable(flag),())),notice).
warning_raise(shared,positive_message,variable(flag),positive).
warning_raise(shared,negative_message,operation(lnot,(variable(flag),())),negative).
