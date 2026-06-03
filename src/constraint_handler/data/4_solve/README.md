### Input predicates

\_passed(sugar,DECL). \_passed(correction(add),LBL,DECL).
\_passed(correction(change,REASON),OLD,NEW). \_expression_safe/1.
\_expression_safeQuery/1. type_expression/2. defaultEngine/1. requestEngine/2.
preference_maximizeScore/0.

### Intermediate predicates

\_passed(correction(rem),dummy). \_passed(solve,DECL). \_passed(solve,NDECL).
\_passed(compile,DECL). \_passed(ground,DECL). \_passed(propagator,DECL).
\_passed((compile;ground;propagator;none),warning_forbid/2).
\_passed((compile;ground;propagator;none),warning_ignore/2).
\_solve_corrected/1. \_label/1. \_label/2. engine/2. \_phase_active/1.
\_main_engine/1. \_main_defaultEngine/1. \_main_defaultEngineProvided/0.
\_main_requestedEngine/1. \_main_solverIdentifiers/1. \_variable_declare/3.
\_variable_domain/2. \_variable_hasDomain/1. \_variable_indexedDomain/3.
\_variable_guess/2. \_variable(ground,VAR). \_ge_assign/3. \_ge_set_assign/3.
\_ge_set_declare/2. \_ge_setAssignsAux/3. \_ge_setAssigns/2.
\_ge_enumeratedVariables/2. \_ge_mapAux/3. \_ge_mapped/2. \_ge_eval_exec/3.
ge_result/2. ge_value/2. \_direct_implode/1. \_direct_imploded/2.
\_expression(compile,EXPR). \_expression(ground,EXPR). \_se_assign/3.
\_expression_pythonEval/2. \_expression_eval_exec/2.
\_expression_dynamicTainted/1. \_argument_value/2. \_direct_queryArgsValues/3.
\_direct_compArg/3. \_computeIdx/2. \_computeIdx/3. \_computedIdx/2.
\_\_computedIdx/2. \_direct_needs_args_list/2. \_direct_args_list_aux/3.
\_direct_args_list/2. \_lambda_aux/2. \_length/2. \_direct_implodeTupleAux/3.
\_int_add/3. \_int_mult/3. \_type_extensionalEquality/1.
\_type_extensionalOrder/1. \_tupleComp/5. \_tuple_pair/5. \_tupleEqAux/3.
\_direct_lazy/1. \_optimize_maximizeSum/4. \_optimize_precision/2.
\_optimize_se_component/3. \_set_declare/2. \_set_assign/3.
\_set_eqMissingEntry/1. \_set_subsetMissingEntry/1. \_set_makeIndex/1.
\_set_foldStep/3. \_set_index/3. \_set_lastIndex/2. \_set_implode/1.
\_set_as_list_aux/3. \_set_imploded/2. \_multimap_declare/2.
\_multimap_assign/4. \_multimap_add/3. \_multimap_has/3.
\_multimap_representative/4. \_multimap_entry/3. \_multimap_eqMissingEntry/1.
\_multimap_makeIndex/1. \_multimap_foldStep/3. \_multimap_index/4.
\_multimap_lastIndex/2. \_preference_expressionScore/2.
\_preference_expression/1. \_preference_index/2. \_preference_potentialAux/2.
\_preference_potentialScore/1. representation/2. order/4.
higher_assigned_domain/3. propagator_bool_evaluate/2. propagator_ensure/2.
propagator_evaluate/3. propagator_variable_declare/3.
propagator_variable_domain/3. propagator_variable_define/3.
propagator_set_declare/2. propagator_set_assign/3. propagator_set_baseDomain/3.
propagator_multimap_assign/4. propagator_multimap_declare/2.
propagator_optimize_maximizeSum/4. propagator_optimize_precision/2.
propagator_warning_forbid/2. propagator_warning_ignore/2.

### Output predicates

\_passed(compile,bool_evaluate/2). \_passed(ground,bool_evaluate/2).
\_passed(propagator,bool_evaluate/2). \_se_value/2. \_set_contains/2.
\_warning/3. direct_query/1. evaluated/3. multimap_value/3. preference_score/1.
