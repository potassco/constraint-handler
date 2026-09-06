evaluate(operation(getOrElse,(val(int,1),(val(int,2),())))).
evaluate(operation(getOrElse,(val(none,none),(val(int,2),())))).
evaluate(operation(getOrElse,(val(none,none),(val(none,none),())))).
evaluate(operation(getOrElse,(val(int,1),(val(none,none),())))).
evaluate(operation(getOrElse,(val(bool,true),(val(int,2),())))).
evaluate(operation(getOrElse,(val(bool,false),(val(int,2),())))).
