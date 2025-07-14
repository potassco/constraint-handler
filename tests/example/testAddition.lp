#include "includeAll.lp".

assign(assign_x, x, val(int,20)).
assign(assign_y, y, operation(add, (variable(x), (val(int,10), ())))).
