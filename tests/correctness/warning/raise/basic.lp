warning_raise(unconditional).
warning_raise(message_only,details(7)).
warning_raise(conditional,none,val(bool,true)).
warning_raise(labeled,details(8),val(bool,true),notice).
warning_raise(inactive,none,val(bool,false)).
warning_raise(failed,none,bad).
warning_raise(folded,operation(eq,(val(int,1),(val(int,2),()))),operation(eq,(val(int,1),(val(int,1),()))),comparison).
