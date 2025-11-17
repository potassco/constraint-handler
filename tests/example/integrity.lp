#include "includeAll.lp".

1 { assign(assign_x,x,val(bool,(true;false))) } 1.
1 { assign(assign_y,y,V) : V=(val(bool,(true;false));val(none,none)) } 1.
1 { assign(assign_z,z,val(bool,(true;false))) } 1.

ensure(dummy,operation(conj,(variable(x),(operation(lnot,(variable(y),())),())))).
