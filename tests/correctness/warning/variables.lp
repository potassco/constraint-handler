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

%%% raises warning(variable(multipleDefinitions),(d_x,(f_x,())),(x,operation(lnot,(variable(itsfine),())),operation(snot,(variable(itsfine),()))))
variable_define(x,operation(lnot,(variable(itsfine),())),d_x).
variable_define(x,operation(snot,(variable(itsfine),())),d_x).
variable_define(x,operation(wnot,(variable(itsfine),())),d_x).

%%% raises warning(variable(multipleDefinitions),(d_y1,(d_y2,())),(y,variable(itsfine),variable(itsfine)))
variable_define(y,variable(itsfine),d_y1).
variable_define(y,variable(itsfine),d_y2).
variable_define(y,variable(itsfine),d_y3).

%%% raises warning(variable(multipleDefinitions),(d_z1,(d_z2,())),(z,variable(itsfine),operation(lnot,(variable(itsfine),()))))
variable_define(z,variable(itsfine),d_z1).
variable_define(z,operation(lnot,(variable(itsfine),())),d_z2).
variable_define(z,operation(snot,(variable(itsfine),())),d_z3).
variable_define(z,operation(wnot,(variable(itsfine),())),d_z4).
