### Input predicates

_phase_active(type_check).
_passed(sugar,LBL,variable_declare/2).
_passed(sugar,LBL,variable_define/2).
_passed(sugar,LBL,variable_domain/2).
_passed(sugar,LBL,variable_interface(X)).
_expression(sugar,EXPR).
_expression_operationIndex(sugar,EXPR,IDX,ARG).
_expression_operationLength(sugar,EXPR,N).
_main_solverIdentifiers/1.
_operator_variadic/1.
_operator_variadicAccepts/2.
_operator_variadicEmptyReturns/2.
_parameter_value/2.
_type/1.
_variable(sugar,X).
operator_declare/3.
operator_declare_variadic/4.
type_query/1.

### Intermediate predicates

_expression(type_check,EXPR).
_expression_sequence(type_check,EXPR).
_expression_sequenceIndex(type_check,EXPR,IDX,ARG).
_expression_sequenceLength(type_check,EXPR,N).
_operator_pythonExtract/1.
_type_expression/2.
_type_expressions/2.
_type_expressionsArgT/3.
_type_expressionsAux/3.
_type_nonMinimal/2.
_type_normalizeQuery/1.
_type_pythonExtract/5.
_type_pythonExtractArgs/1.
_type_pythonExtractAux/3.
_type_pythonTypeExtractResult/2.
_type_variable/2.
_type_variadicListAux/5.
_type_warning/2.

### Output predicates

_correction_expression(type_check,EXPR,bad).
_warning/3.
type_expression/2.
type_variable/2.
