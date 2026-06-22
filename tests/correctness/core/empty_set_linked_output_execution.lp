% Temporary debug variant of empty_set_linked_output_execution.
% Keep the same setup, but probe the relevant subexpressions via evaluate/2
% instead of enforcing the implication, so compile2 stays satisfiable.

set_declare(b,s0(b)).
variable_define(a,a,val(bool,true)).
variable_define(b,b,operation(if,(variable(a),(variable(s0(b)),())))).
execution_run(e,e).
execution_declare(e,e,assign("y",operation(set_make,())),(),("y",())).

bool_evaluate(variable(a)).
evaluate(hasValue,(variable(execution_output(e,"y")),())).
evaluate(conj,(variable(a),(operation(hasValue,(variable(execution_output(e,"y")),())),()))).
evaluate(length,(variable(b),())).
evaluate(length,(variable(execution_output(e,"y")),())).
evaluate(subset,(variable(execution_output(e,"y")),(variable(b),()))).
evaluate(subset,(variable(b),(variable(execution_output(e,"y")),()))).
evaluate(eq,(variable(b),(operation(set_make,()),()))).
evaluate(eq,(variable(execution_output(e,"y")),(operation(set_make,()),()))).

% First failing probe under compile2; enabling it makes this debug case UNSAT.
% evaluate(eq,(variable(execution_output(e,"y")),(variable(b),()))).
% evaluate(limp,
%   (operation(conj,(variable(a),(operation(hasValue,(variable(execution_output(e,"y")),())),()))),
%    (operation(eq,(variable(execution_output(e,"y")),(variable(b),()))),()))).
