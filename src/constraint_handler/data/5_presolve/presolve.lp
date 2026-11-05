_passed(presolve,LBL,DECL) :- _passed(sugar,LBL,DECL), #false : _passed(correction(REASON,rem),LBL,DECL).
_passed(presolve,LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).

ch_core(DECL,LBL) :- _passed(presolve,LBL,DECL).
