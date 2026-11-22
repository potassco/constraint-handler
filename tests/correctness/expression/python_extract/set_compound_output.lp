phase_request(constantFolding,false).

variable_declare(inner,set).
set_assign(inner,val(int,2)).
set_assign(inner,val(int,3)).

variable_declare(nested,set).
set_assign(nested,variable(inner)).

variable_declare(pairs,set).
set_assign(pairs,(val(int,1),variable(inner))).

variable_define(python_nested,operation(pythonExtract("","frozenset({frozenset({2, 3})})"),())).
variable_define(python_pairs,operation(pythonExtract("","frozenset({(1, frozenset({2, 3}))})"),())).
variable_define(nested_equal,operation(eq,(variable(python_nested),(variable(nested),())))).
variable_define(pairs_equal,operation(eq,(variable(python_pairs),(variable(pairs),())))).