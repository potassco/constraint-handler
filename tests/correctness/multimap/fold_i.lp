variable_declare(entries,multimap).
multimap_assign(entries,val(int,2),val(int,3)).
multimap_assign(entries,val(int,2),val(int,5)).
multimap_assign(entries,val(int,4),val(int,6)).
variable_declare(empty,multimap).

variable_define(Result,operation(multimap_fold_i,(Callback,(variable(Map),(val(int,7),()))))) :-
    (Result,Map) = (folded,entries;empty_fold,empty),
    Callback = lambda((key,(value,(accumulator,()))),Body),
    Body = operation(add,(variable(accumulator),(Product,(variable(value),())))),
    Product = operation(mult,(variable(key),(val(int,10),()))).
