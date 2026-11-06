warning_raise(unconditional).
warning_raise(conditional,val(bool,true)).
warning_raise(labeled,val(bool,true),notice).
warning_raise(inactive,val(bool,false)).
warning_raise(failed,bad).
warning_raise(folded,operation(eq,(val(int,1),(val(int,1),()))),comparison).
