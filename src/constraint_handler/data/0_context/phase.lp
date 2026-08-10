%%%%%%%%%%%%%%%%% phases
#defined phase_request/2.

_phase(solve).
_phase_default(solve,true).
_phase(constantFolding).
_phase_default(constantFolding,true).
_phase(float_normalize).
_phase_default(float_normalize,true).
_phase(safe).
_phase_default(safe,true).
_phase(statement_wellformedCheck).
_phase_default(statement_wellformedCheck,true).
_phase(type_check).
_phase_default(type_check,false).
_phase(wf_check).
_phase_default(wf_check,true).

_phase_userRequest(PHASE) :- phase_request(PHASE,BOOL), _phase(PHASE).
_phase_active(PHASE) :- _phase_default(PHASE,true), not _phase_userRequest(PHASE).
_phase_active(PHASE) :- phase_request(PHASE,true).
