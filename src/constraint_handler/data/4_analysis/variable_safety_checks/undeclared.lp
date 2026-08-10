_variable_declared(X,D) :- _passed(sugar,LBL,variable_declare(X,D)).

_variable_declareRequired(LBL,X,definition) :- _passed(sugar,LBL,variable_define(X,E)), not _variable_declared(X,definition).
_variable_declareRequired(LBL,X,fromFacts) :- _passed(sugar,LBL,variable_domain(X,E)), not _variable_declared(X,fromFacts).
_variable_declareRequired(LBL,X,set) :- _passed(sugar,LBL,set_baseDomain(X,E)), not _variable_declared(X,set).
_variable_declareRequired(LBL,X,set) :- _passed(sugar,LBL,set_assign(X,E)), not _variable_declared(X,set).
_variable_declareRequired(LBL,X,multimap) :- _passed(sugar,LBL,multimap_assign(X,K,V)), not _variable_declared(X,multimap).

_warning(variable(undeclared),LBL,(X,D)) :- _variable_declareRequired(LBL,X,D), not _variable_declared(X,D).
_passed(correction(undeclared,add),LBL,variable_declare(X,D)) :- _variable_declareRequired(LBL,X,D), not _variable_declared(X,D).

_warning(variable(undeclared),(),X) :- _variable(sugar,X), #false: _variable_declared(X,D); #false: _variable_declareRequired(LBL,X,D).
_passed(correction(undeclared,add),_internal,(variable_declare(X,definition);variable_define(X,bad))) :- _variable(sugar,X), #false: _variable_declared(X,D); #false: _variable_declareRequired(LBL,X,D).
