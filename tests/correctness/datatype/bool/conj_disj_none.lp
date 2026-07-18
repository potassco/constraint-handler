%%% binary conjunction/disjunction with none involved

evaluate(conj,(val(bool,false),(val(none,none),()))).
evaluate(conj,(val(none,none),(val(bool,false),()))).
evaluate(conj,(val(bool,true),(val(none,none),()))).
evaluate(conj,(val(none,none),(val(bool,true),()))).
evaluate(conj,(val(none,none),(val(none,none),()))).

evaluate(disj,(val(bool,false),(val(none,none),()))).
evaluate(disj,(val(none,none),(val(bool,false),()))).
evaluate(disj,(val(bool,true),(val(none,none),()))).
evaluate(disj,(val(none,none),(val(bool,true),()))).
evaluate(disj,(val(none,none),(val(none,none),()))).
