#include "includeAll.lp".

%%% doesn't raise anything
variable_declare(d_i,itsfine,boolDomain).
variable_declare(d_i,itsfine,boolDomain).

variable_declare(d_i2,itsfine2,fromFacts).
variable_domain(itsfine2,val(symbol,red)).
variable_domain(itsfine2,val(symbol,black)).

%%% raises warning(variable(emptyDomain),(d_a,()),a) and warning(variable(emptyDomain),(d_b,()),b)
variable_declare(d_a,a,fromList(())).
variable_declare(d_b,b,fromFacts).

%%% raises warning(variable(undeclared),(),c) and warning(variable(undeclared),(),d)
variable_domain(c,val(symbol,(red;green;blue))).
variable_domain(d,val(int,0..5)).

%%% raises warning(variable(multipleDeclarations),(d_t,(d_t,())),(t,fromList((val(symbol,green),(val(symbol,blue),()))),fromList((val(symbol,red),()))))
variable_declare(d_t,t,fromList((val(symbol,red),()))).
variable_declare(d_t,t,fromList((val(symbol,green),(val(symbol,blue),())))).

%%% raises warning(variable(multipleDeclarations),(d_u,(_u,())),(u,boolDomain,fromFacts))
variable_declare(d_u,u,fromFacts).
variable_declare(d_u,u,boolDomain).
variable_declare(d_u,u,fromList((val(symbol,red),()))).

%%% raises warning(variable(multipleDeclarations),(d_v1,(d_v2,())),(v,fromFacts,fromFacts))
variable_declare(d_v1,v,fromFacts).
variable_declare(d_v2,v,fromFacts).
variable_declare(d_v3,v,fromFacts).
variable_domain(v,val(symbol,green)).

%%% raises warning(variable(multipleDeclarations),(d_w1,(d_w2,())),(w,fromFacts,fromFacts))
variable_declare(d_w1,w,fromFacts).
variable_declare(d_w2,w,fromFacts).
variable_declare(d_w3,w,boolDomain).
variable_declare(d_w4,w,fromList((val(symbol,blue),()))).

%%% raises warning(variable(multipleDefinitions),(d_x,(f_x,())),(x,operation(lnot,(variable(itsfine),())),operation(snot,(variable(itsfine),()))))
variable_define(d_x,x,operation(lnot,(variable(itsfine),()))).
variable_define(d_x,x,operation(snot,(variable(itsfine),()))).
variable_define(d_x,x,operation(wnot,(variable(itsfine),()))).

%%% raises warning(variable(multipleDefinitions),(d_y1,(d_y2,())),(y,variable(itsfine),variable(itsfine)))
variable_define(d_y1,y,variable(itsfine)).
variable_define(d_y2,y,variable(itsfine)).
variable_define(d_y3,y,variable(itsfine)).

%%% raises warning(variable(multipleDefinitions),(d_z1,(d_z2,())),(z,variable(itsfine),operation(lnot,(variable(itsfine),()))))
variable_define(d_z1,z,variable(itsfine)).
variable_define(d_z2,z,operation(lnot,(variable(itsfine),()))).
variable_define(d_z3,z,operation(snot,(variable(itsfine),()))).
variable_define(d_z4,z,operation(wnot,(variable(itsfine),()))).
