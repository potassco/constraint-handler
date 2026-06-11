### Input predicates

_passed(defaultArgs,LBL,execution_declare/4).
_passed(defaultArgs,LBL,execution_run/1).

### Intermediate predicates

_execution_declare/5.
_execution_input_var/2.
_execution_isRunning/1.
_execution_ou_proj/2.
_execution_outputVar/3.
_statement_query/3.
_statement_querySSA/4.
_statement_changed/2.
_statement_context/3.
_statement_condition/2.
_statement_countVars/2.
_statement_definedLatest/2.
_statement_ensure/2.
_statement_hasContext/2.
_statement_indexedVar/3.
_statement_introduce/3.
_statement_latest/3.
_statement_pythonInputMap/2.
_statement_pythonInputMapAux/3.
_statement_pythonVarsResult/3.
_statement_scoped/3.
_expression_context/4.
_expression_contextualized/3.
_expression_contextualizedListAux/4.
_expression_querySSA/3.
_expression_sequenceHelper/2.
_length/3.
_expression_index/4.
_expression_isTuple/4.
_main_solverIdentifiers/1.

### Output predicates

_passed(ssa,LBL,variable_define/2).
_passed(ssa,LBL,variable_declare/2).
_passed(ssa,LBL,ensure/1).
_variable(ssa,execution_input/2).
_statement_wellformed/1.
_statement_internalVariable/1.
_warning/3.
