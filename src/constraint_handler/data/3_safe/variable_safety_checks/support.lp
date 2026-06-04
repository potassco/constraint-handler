_variable_exists(sugar,X) :- _passed(sugar,variable_declare(LBL,X,D)).

_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=variable_declare(LBL,X,D).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=variable_define(LBL,X,D).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=variable_domain(LBL,X,D).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=set_declare(LBL,X).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=set_assign(LBL,X,D).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=set_baseDomain(LBL,X,D).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=multimap_declare(LBL,X).
_variable_involve(defaultArgs,X,DECL) :- _passed(defaultArgs,DECL), DECL=multimap_assign(LBL,X,D,E).

_variable_involve(sugar,X,DECL) :- _passed(sugar,DECL), DECL=variable_declare(LBL,X,D).
_variable_involve(sugar,X,DECL) :- _passed(sugar,DECL), DECL=variable_define(LBL,X,D).
_variable_involve(sugar,X,DECL) :- _passed(sugar,DECL), DECL=variable_domain(LBL,X,D).
_variable_involve(sugar,X,DECL) :- _passed(sugar,DECL), DECL=set_assign(LBL,X,D).
_variable_involve(sugar,X,DECL) :- _passed(sugar,DECL), DECL=set_baseDomain(LBL,X,D).
_variable_involve(sugar,X,DECL) :- _passed(sugar,DECL), DECL=multimap_assign(LBL,X,D,E).
