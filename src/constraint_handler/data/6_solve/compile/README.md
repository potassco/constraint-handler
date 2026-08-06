### Input predicates

_passed(compile,LBL,DECL).
_passed(sugar,LBL,set_baseDomain/2).
_expression_tupleLength(compile,EXPR,N).
_expression_tupleIndex(compile,EXPR,IDX,ARG).
_expression_operationIndex(compile,EXPR,IDX,ARG).
_expression_operationIndex(sugar,EXPR,IDX,ARG).
_expression_operationOperator(sugar,EXPR,OP).
_expression_safe/1.
_expression_safeQuery/1.
_operator_recoverable/1.
_main_solverIdentifiers/1.
_type_extensionalEquality/1.
_type_extensionalOrder/1.
_type_representation/2.
type_expression/2.
engine(LBL,compile).

### Intermediate predicates

_expression_pythonEval/2.
_expression_dynamicTainted/1.
_argument_value/2.
_direct_queryArgsValues/3.
_computeIdx/2. _computeIdx/3.
_computedIdx/2.
_direct_compArg/3.
_direct_args_list_aux/3.
_direct_args_list/2.
_direct_implode/1.
_direct_imploded_args_aux/3.
_direct_implodeTupleAux/3.
_direct_lazy/1.
_direct_needs_args_list/2.
_direct_tupleValuesAux/3.
_expression_eval_exec/2.
_expression(compile,EXPR).
_int_add/3.
_int_mult/3.
_isTuple/2. _isTuple/4.
_lambda_aux/2.
_length/2.
_multimap_add/3.
_multimap_has/3.
_multimap_representative/4.
_multimap_entry/3.
_multimap_eqMissingEntry/1.
_multimap_makeIndex/1.
_multimap_foldStep/3.
_multimap_index/4.
_multimap_lastIndex/2.
_operator_needsPython/2. _operator_needsPython/3.
_set_eqMissingEntry/1.
_set_subsetMissingEntry/1.
_set_makeIndex/1.
_set_foldStep/3.
_set_index/3.
_set_lastIndex/2.
_set_implode/1.
_set_as_list_aux/3.
_set_imploded/2.
_tupleComp/5.
_tuple_pair/5.
_tupleEqAux/3.

### Output predicates

_passed(correction(REASON,add),LBL,DECL).
direct_query/1.
evaluated/3.
_se_value/2.
_set_assign/3.
_set_contains/2.
_direct_imploded/2.
_warning/3.
multimap_value/3.
