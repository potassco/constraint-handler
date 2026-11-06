_variable_declared(X,D) :- _passed(sugar,LBL,variable_declare(X,D,C)).

_variable_declareRequired(LBL,X,open) :- _passed(sugar,LBL,variable_assign(X,E)), not _variable_declared(X,open).
_variable_declareRequired(LBL,X,open) :- _passed(sugar,LBL,variable_choice(X,E)), not _variable_declared(X,open).
_variable_declareRequired(LBL,X,open) :- _passed(sugar,LBL,variable_default(X,E,C,P)), not _variable_declared(X,open).
_variable_declareRequired(LBL,X,definition) :- _passed(sugar,LBL,variable_define(X,E,C)), not _variable_declared(X,definition).
_variable_declareRequired(LBL,X,fromFacts) :- _passed(sugar,LBL,variable_domain(X,E,C)), not _variable_declared(X,fromFacts).
_variable_declareRequired(LBL,X,set) :- _passed(sugar,LBL,set_baseDomain(X,E,C)), not _variable_declared(X,set).
_variable_declareRequired(LBL,X,set) :- _passed(sugar,LBL,set_assign(X,E,C)), not _variable_declared(X,set).
_variable_declareRequired(LBL,X,multimap) :- _passed(sugar,LBL,multimap_assign(X,K,V)), not _variable_declared(X,multimap).

ch_core(warning_raise(variable(undeclared),(X,D),val(bool,true)),LBL) :- _variable_declareRequired(LBL,X,D), not _variable_declared(X,D).
_passed(correction(undeclared,add),LBL,variable_declare(X,D,val(bool,true))) :- _variable_declareRequired(LBL,X,D), not _variable_declared(X,D).

ch_core(warning_raise(variable(undeclared),X,val(bool,true)),()) :- _variable(sugar,X), #false: _variable_declared(X,D); #false: _variable_declareRequired(LBL,X,D).
_passed(correction(undeclared,add),_internal,(variable_declare(X,definition,val(bool,true));variable_define(X,bad,val(bool,true)))) :- _variable(sugar,X), #false: _variable_declared(X,D); #false: _variable_declareRequired(LBL,X,D).

_variable_definition_completion(X,LBL) :- _passed(sugar,LBL,variable_declare(X,definition,C)), #false : _passed(sugar,_,variable_define(X,E,(C;val(bool,true)))).
_variable_definition_completion(X,LBL) :- _variable_declareRequired(LBL,X,definition), #false : _passed(sugar,_,variable_define(X,E,val(bool,true))).

_passed(correction(missing_definition,add),LBL,variable_declare(loc(has_active_definition(X)),fromFacts,val(bool,true))) :- _variable_definition_completion(X,LBL).
_passed(correction(missing_definition,add),LBL,variable_domain(loc(has_active_definition(X)),val(bool,false),val(bool,true))) :- _variable_definition_completion(X,LBL).
_passed(correction(missing_definition,add),LBL,variable_domain(loc(has_active_definition(X)),val(bool,true),C)) :- _variable_definition_completion(X,LBL), _passed(sugar,_,variable_define(X,E,C)).
_passed(correction(missing_definition,add),LBL,check(operation(limp,(C,(variable(loc(has_active_definition(X))),()))))) :- _variable_definition_completion(X,LBL), _passed(sugar,_,variable_define(X,E,C)).
_passed(correction(missing_definition,add),LBL,variable_define(X,bad,operation(lnot,(variable(loc(has_active_definition(X))),())))) :- _variable_definition_completion(X,LBL).
