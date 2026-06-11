### Input predicates

_phase_active(type_check).
_passed(sugar,LBL,variable_declare/2).
_passed(sugar,LBL,variable_define/2).
_passed(sugar,LBL,variable_domain/2).
_expression(sugar,EXPR).
_expression_operationIndex(sugar,EXPR,IDX,ARG).
_expression_operationLength(sugar,EXPR,N).
operator_declare/3.
operator_declare_variadic/4.
type_query/1.

### Intermediate predicates

_expression_sequence(type_check,EXPR).
_expression_sequenceIndex(type_check,EXPR,IDX,ARG).
_expression_sequenceLength(type_check,EXPR,N).
_expression_typeQuery/1.
_type_list/2.
_type_listArgT/3.
_type_listAux/3.
_type_operator/2.
_type_variable/2.
_type_variadicListAux/5.
operator_variadic/2.
type_expressionTyped/1.
type_variable/2.

### Output predicates

_type/1.
_warning(type(failed_operation),(),(O,ARGS)).
type_expression/2.
