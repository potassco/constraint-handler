% Regression: thresholded set overapproximations must stay within operation-specific candidate atoms.

set_declare(left).
set_baseDomain(left,val(int,1..8)).

set_declare(right).
set_baseDomain(right,val(int,5..12)).

variable_define(union_lr,operation(union,(variable(left),(variable(right),())))).
variable_define(inter_lr,operation(inter,(variable(left),(variable(right),())))).
variable_define(diff_lr,operation(diff,(variable(left),(variable(right),())))).

evaluate(subset,(variable(left),(variable(right),()))).
