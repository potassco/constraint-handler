
%%%%%% warning atoms
%_passed((sugar;wf_check),warning_forbid(LBL,KIND)) :- _passed(defaultArgs,warning_forbid(LBL,KIND)).
%_passed((sugar;wf_check),warning_ignore(LBL,KIND)) :- _passed(defaultArgs,warning_ignore(LBL,KIND)).
_passed(sugar,warning_forbid(LBL,KIND)) :- _passed(defaultArgs,warning_forbid(LBL,KIND)).
_passed(sugar,warning_ignore(LBL,KIND)) :- _passed(defaultArgs,warning_ignore(LBL,KIND)).
