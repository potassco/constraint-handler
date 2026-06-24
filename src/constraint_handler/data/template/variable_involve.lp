_variable_exists(sugar,X) :- _passed(sugar,LBL,variable_declare(X,D)).

_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=variable_declare(X,D).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=variable_define(X,D).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=variable_domain(X,D).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=set_declare(X).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=set_assign(X,D).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=set_baseDomain(X,D).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=multimap_declare(X).
_variable_involve(defaultArgs,LBL,X,DECL) :- _passed(defaultArgs,LBL,DECL), DECL=multimap_assign(X,D,E).

_variable_involve(sugar,LBL,X,DECL) :- _passed(sugar,LBL,DECL), DECL=variable_declare(X,D).
_variable_involve(sugar,LBL,X,DECL) :- _passed(sugar,LBL,DECL), DECL=variable_define(X,D).
_variable_involve(sugar,LBL,X,DECL) :- _passed(sugar,LBL,DECL), DECL=variable_domain(X,D).
_variable_involve(sugar,LBL,X,DECL) :- _passed(sugar,LBL,DECL), DECL=set_assign(X,D).
_variable_involve(sugar,LBL,X,DECL) :- _passed(sugar,LBL,DECL), DECL=set_baseDomain(X,D).
_variable_involve(sugar,LBL,X,DECL) :- _passed(sugar,LBL,DECL), DECL=multimap_assign(X,D,E).
