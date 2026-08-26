evaluate(getOrElse,(val(int,1),(val(int,2),()))).
evaluate(getOrElse,(val(none,none),(val(int,2),()))).
evaluate(getOrElse,(val(none,none),(val(none,none),()))).
evaluate(getOrElse,(val(int,1),(val(none,none),()))).
evaluate(getOrElse,(val(bool,true),(val(int,2),()))).
evaluate(getOrElse,(val(bool,false),(val(int,2),()))).
