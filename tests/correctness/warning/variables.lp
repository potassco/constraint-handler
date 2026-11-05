%%% doesn't raise anything
variable_declare(itsfine,boolDomain,val(bool,true),d_i).
variable_declare(itsfine,boolDomain,val(bool,true),d_i).

variable_declare(itsfine2,fromFacts,val(bool,true),d_i2).
variable_domain(itsfine2,val(symbol,red)).
variable_domain(itsfine2,val(symbol,black)).

%%% raises warning(variable(emptyDomain),(d_a,()),a) and warning(variable(emptyDomain),(d_b,()),b)
variable_declare(b,fromFacts,val(bool,true),d_b).

%%% raises warning(variable(multipleDeclarations),(d_u,(_u,())),(u,boolDomain,fromFacts))
variable_declare(u,fromFacts,val(bool,true),d_u).
variable_declare(u,boolDomain,val(bool,true),d_u).

%%% raises warning(variable(multipleDeclarations),(d_v1,(d_v2,())),(v,fromFacts,fromFacts))
variable_declare(v,fromFacts,val(bool,true),d_v1).
variable_declare(v,fromFacts,val(bool,true),d_v2).
variable_declare(v,fromFacts,val(bool,true),d_v3).
variable_domain(v,val(symbol,green)).

%%% raises warning(variable(multipleDeclarations),(d_w1,(d_w2,())),(w,fromFacts,fromFacts))
variable_declare(w,fromFacts,val(bool,true),d_w1).
variable_declare(w,fromFacts,val(bool,true),d_w2).
variable_declare(w,boolDomain,val(bool,true),d_w3).
