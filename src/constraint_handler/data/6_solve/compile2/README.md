### inputs

_passed(compile2, LBL, Declaration)

Declaration can be:

%%% variable and domain definition
_passed(compile2, LBL, variable_declare(Var, fromFacts)). % the variable is connected to a domain, unecessary
_passed(compile2, LBL, variable_domain(Var, Expr)) % all possible expressions

_passed(compile2, LBL, variable_declare(Var, set)). % variable is declared as a set
_passed(compile2, LBL, set_baseDomain(Var, Expr)).

_passed(compile2, LBL, variable_declare(Var, definition)). % not used, define is enough
_passed(compile2, LBL, variable_define(Var, Expr))  % Expr is assign to Var

_passed(compile2, LBL, set_assign(Var, Expr)) % Expr is assigned to Var, but Var is a set


%%% constraints, evaluate, preference, and optimize statements
_passed(compile2,LBL,share_value(E))

%%% ignore
warning_ignore

## expressions
Expr = operation(Operator, ExprList)
Expr = val(Type, Value)
Expr = variable(Name)
Expr = bad
Expr = (Expr1, Expr2, Expr3, ...)
ExprList = (Expr1, (Expr2, (Expr3, ...., ())))

operation(add, (1, (42, operation(mult, 3))))

### Input predicates

_passed(compile2,LBL,DECL).
_expression_operationIndex(compile2,EXPR,IDX,ARG).
_expression_operationLength(compile2,EXPR,N).
_expression_tupleIndex(compile2,EXPR,IDX,ARG).
_expression_tupleLength(compile2,EXPR,N).
_type_dynamic(compile2,EXPR,T).
_main_solverIdentifiers/1.

### Intermediate predicates

_expression(compile2,EXPR).
_expression_badArgument/1.
_expression_is_value/1.
_float_eq_value/2.
_float_has_zero/1.
_non_integer_operation/1.
_python_evaluation_input/4.
_python_evaluation_result/2.
_se_domain/2.
_se_is_set/1.
_set_bad/1.
_set_choice_contains/2.
_set_choice_value/2.
_top_level_expression/1.
var_has_domain/1.

### Output predicates

_se_value/2.
_set_contains/2.
