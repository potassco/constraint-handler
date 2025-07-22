assign(cycle_1, a, variable(b)).
assign(cycle_1_2, b, operation(add, (variable(c), (variable(d), ())))).
assign(cycle_1, c, variable(a)).
assign(cycle_2, d, variable(e)).
assign(cycle_2, e, variable(b)).