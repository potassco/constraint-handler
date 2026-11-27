_warning(variable(badValue),LBL,X) :-
	_se_value(variable(X),bad),
	ch_post(variable_interface(X),LBL),
  _variable_declared(X),
  not _variable_definition_inactive(X).
