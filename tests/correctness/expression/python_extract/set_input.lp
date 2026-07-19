variable_define(pool,operation(set_make,(val(int,1),(val(int,2),(val(int,5),()))))).
variable_define(has_two,operation(pythonExtract("present = needle in pool","present"),((val(string,"needle"),val(int,2)),((val(string,"pool"),variable(pool)),())))).
variable_define(missing_four,operation(pythonExtract("present = needle in pool","not present"),((val(string,"needle"),val(int,4)),((val(string,"pool"),variable(pool)),())))).

#show value/2.
