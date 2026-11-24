variable_define(pair,(val(string,"key"),val(int,7))).
variable_define(from_pair,operation(multimap_make,(variable(pair),()))).
variable_define(from_pair_count,operation(countEntries,(variable(from_pair),()))).
