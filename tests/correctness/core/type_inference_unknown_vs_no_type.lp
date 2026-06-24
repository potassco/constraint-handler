variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).

% Unknown/unsupported inferred type from Python expression.
variable_define(list_var,operation(pythonExtract("tmp=[1,2,3]","tmp"),())).

% Unknown function call keeps type inference in the unsupported bucket.
variable_define(mystery_call,operation(pythonExtract("tmp=mystery(x)","tmp"),((val(string,"x"),variable(x)),()))).

% Known operator with incorrect argument types should have no valid type.
variable_define(bad_add,operation(add,(val(string,"foo"),(val(bool,true),())))).
