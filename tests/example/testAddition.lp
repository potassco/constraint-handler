#include "includeAll.lp".

assign(assign_x, x, constant(int(20))).
assign(assign_y, y, operation(add, (variable(x), (constant(int(10)), ())))).
