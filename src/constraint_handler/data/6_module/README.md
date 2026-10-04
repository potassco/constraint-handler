### Input predicates

default_mode/1.
preference_maximizeScore/0.
_engine/2.
_bool_evaluated/2.
_passed(sugar,LBL,preference_holds/2).
_phase_active/1.
ch_core(bool_evaluate/1,LBL).
ch_core(ensure/1,LBL).
ch_core(preference_holds/2,LBL).
ch_core(set_baseDomain/2,LBL).
ch_core(variable_assign/2,LBL).
ch_core(variable_declare/2,LBL).
ch_core(variable_default/3,LBL).
ch_solve(variable_assign/2,LBL).
ch_solve(variable_choice/2,LBL).
ch_solve(variable_declare/2,LBL).
ch_solve(variable_default/4,LBL).
_se_value/2.

### Intermediate predicates

_default_apply/3.
_default_connect/2.
_default_dependVariable/2.
_default_ensureVariable/2.
_default_mode/1.
_default_modeProvided/0.
_default_possibleMode/1.
_preference_expression/1.
_preference_index/2.
_preference_potentialAux/2.
_preference_potentialScore/1.
_preference_expressionScore/2.
_set_baseDomain/3.
_bool_evaluate/2.

### Output predicates

_bool_evaluated/2.
_warning/3.
_se_value/2.
ch_solve(set_assign/3,LBL).
ch_solve(share_value/1,LBL).
ch_solve(variable_declare/2,LBL).
ch_solve(variable_domain/2,LBL).
bool_evaluated/2.
preference_score/1.
propagator_bool_evaluate/2.
