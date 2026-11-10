variable_declare(entries,multimap).
multimap_assign(entries,val(int,1),val(int,10)).
multimap_assign(entries,val(int,1),val(int,20)).
multimap_assign(entries,val(int,2),val(int,30)).
variable_declare(empty,multimap).

variable_define(present,operation(multimap_find2,(variable(entries),(val(int,1),(val(int,10),()))))).
variable_define(second_value,operation(multimap_find2,(variable(entries),(val(int,1),(val(int,20),()))))).
variable_define(wrong_value,operation(multimap_find2,(variable(entries),(val(int,1),(val(int,30),()))))).
variable_define(missing_key,operation(multimap_find2,(variable(entries),(val(int,3),(val(int,10),()))))).
variable_define(empty_map,operation(multimap_find2,(variable(empty),(val(int,1),(val(int,10),()))))).