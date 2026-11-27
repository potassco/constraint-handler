_warning(variable(badValue),LBL,X) :-
	_se_value(variable(X),bad),
	ch_post(variable_interface(X),LBL),
	_passed(_,_,variable_declare(X,_,C)),
	_bool_evaluated(C,val(bool,true)).
