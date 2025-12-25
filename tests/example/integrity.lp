#include "includeAll.lp".

variable_declare(assign_x,x,boolDomain).
variable_declare(assign_y,y,boolDomain).
variable_declareOptional(y).
variable_declare(assign_z,z,boolDomain).

ensure(dummy,operation(conj,(variable(x),(operation(lnot,(variable(y),())),())))).
