### inputs

_passed(compile, LBL, Declaration)

Declaration can be:

%%% variable and domain definition
_passed(compile, LBL, variable_declare(Var, fromFacts)). % the variable is connected to a domain, unecessary
_passed(compile, LBL, variable_domain(Var, Expr)) % all possible expressions

_passed(compile, LBL, variable_declare(Var, set)). % variable is declared as a set
_passed(compile, LBL, set_baseDomain(Var, Expr)).

_passed(compile, LBL, variable_declare(Var, definition)). % not used, define is enough
_passed(compile, LBL, variable_define(Var, Expr))  % Expr is assign to Var

_passed(compile, LBL, set_assign(Var, Expr)) % Expr is assigned to Var, but Var is a set


%%% constraints
_passed(compile, LBL, ensure(Expr))
_passed(compile, LBL, bool_evaluate(Expr))
%% what about _passed(compile, LBL, evaluate())

%%% preferences and optimize statements
_passed(compile,LBL,optimize_maximizeSum(E,X,P))
_passed(compile,LBL,optimize_precision(PREC,PRIO))

%%% ignore
warning_ignore

## expressions
Expr = operation(Operator, ExprList)
Expr = val(Type, Value)
Expr = variable(Name)
Expr = bad
Expr = (Expr1, Expr2, Expr3, ...)
ExprList = (Expr1, (Expr2, (Expr3, ....))))

operation(add, (1, (42, operation(mult, 3))))


### outputs
_se_value(Expr, Value)
_se_value(Expr, set) % if Expr evaluates to a set
_set_contains(Expr, Value)  % if Expr evaluates to a set, these values are in the set, no nested sets
bool_evaluated(Expr, Value) % true of false for bool_evaluate Expressions ( or bad )