% Regression: python operator with multiple arguments
% Ensures compile-engine implosion + argument list rebuilding works.
% Use value/2 to avoid clingo pretty-print newlines in long evaluated/3 atoms.
%
% Note: do NOT rely on "math" being present in the shared environment.
% The custom_globals test removes it globally for the rest of the pytest run.

variable_define(d,r,operation(python("pow"),(val(float,float("2")),(val(float,float("3")),())))).
