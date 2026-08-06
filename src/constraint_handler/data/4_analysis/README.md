### Input predicates

_passed(defaultArgs,LBL,DECL).
_passed(sugar,LBL,DECL).
_expression(sugar,EXPR).
_variable(sugar,VAR).
_statement_wellformed/1.
_variable_internal(X).
_variable_involve(defaultArgs,LBL,X,DECL).
_variable_involve(sugar,LBL,X,DECL).
_main_solverIdentifiers/1.
_parameter_value/2.
_phase_active/1.
_number(sugar,N).
type_query/1.
operator_declare/3.
operator_declare_variadic/4.

### Intermediate predicates

_deterministic/2.
_expression_domain/2.
_expression_operationIndex/4.
_expression_operationLength/3.
_expression_operationOperator/3.
_expression_sequence/2.
_expression_sequenceIndex/4.
_expression_sequenceLength/3.
_expression_setDomain/4.
_expression_setDomainQuery/2.
_expression_setExpr/4.
_expression_setExprIndex/5.
_expression_tupleDomainAux/3.
_expression_tupleIndex/4.
_expression_typeQuery/1.
_expression_wellformed/1.
_expression_wfQuery/1.
_float_normalizeQuery/1.
_illformed/1. _illformed/2.
_main/1.
_operator_declared/1.
_operator_pythonExtract/1.
_operator_recoverable/1.
_operator_safe/1.
_operator_unsafe/1.
_safe_bad/1.
_type/1.
_type_expressions/2.
_type_expressionsArgT/3.
_type_expressionsAux/3.
_type_list/2.
_type_listArgT/3.
_type_listAux/3.
_type_nonMinimal/2.
_type_normalizeQuery/1.
_type_operator/2.
_type_pythonExtract/5.
_type_pythonExtractArgs/1.
_type_pythonExtractAux/3.
_type_pythonTypeExtractResult/2.
_type_variable/2.
_type_variadicListAux/5.
_type_warning/2.
_variable_declared/2.
_variable_declareRequired/3.
_variable_hasDomain/2.
_variable_multiple/2.
_variable_multipleDeclarations/3.
_variable_multipleDefinitions/3.
_variable_name/2.
_variable_query/2.
_variable_safe/1.
_variable_strip/3.
operator_variadic/2.
type_expressionTyped/1.
type_variable/2.

### Output predicates

_correction_expression/3.
_correction_number/3.
_passed(correction(REASON,add),LBL,DECL).
_passed(correction(REASON,rem),LBL,DECL).
_warning/3.
_expression_safe/1.
_expression_safeQuery/1.
type_expression/2.
