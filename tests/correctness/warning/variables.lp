%%% doesn't raise anything
variable_declare(itsfine,boolDomain,d_i).
variable_declare(itsfine,boolDomain,d_i).

variable_declare(itsfine2,fromFacts,d_i2).
variable_domain(itsfine2,val(symbol,red)).
variable_domain(itsfine2,val(symbol,black)).

%%% raises warning(variable(emptyDomain),(d_a,()),a) and warning(variable(emptyDomain),(d_b,()),b)
variable_declare(b,fromFacts,d_b).

%%% raises warning(variable(multipleDeclarations),(d_u,(_u,())),(u,boolDomain,fromFacts))
variable_declare(u,fromFacts,d_u).
variable_declare(u,boolDomain,d_u).

%%% raises warning(variable(multipleDeclarations),(d_v1,(d_v2,())),(v,fromFacts,fromFacts))
variable_declare(v,fromFacts,d_v1).
variable_declare(v,fromFacts,d_v2).
variable_declare(v,fromFacts,d_v3).
variable_domain(v,val(symbol,green)).

%%% raises warning(variable(multipleDeclarations),(d_w1,(d_w2,())),(w,fromFacts,fromFacts))
variable_declare(w,fromFacts,d_w1).
variable_declare(w,fromFacts,d_w2).
variable_declare(w,boolDomain,d_w3).
