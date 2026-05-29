_main(solve).
_passed(solve,DECL) :- _main(solve), _passed(sugar,DECL), not _solve_corrected(DECL).
_solve_corrected(DECL) :- _main(solve), _passed(correction(REASON),DECL,NDECL).
_solve_corrected(DECL) :- _main(solve), _passed(correction(rem),LBL,DECL).
_passed(solve,NDECL) :- _main(solve), _passed(correction(REASON),DECL,NDECL).
_label(LBL,NDECL) :- _label(LBL,DECL), _passed(correction(REASON),DECL,NDECL).
_label(LBL,DECL) :- _main(solve), _passed(correction(add),LBL,DECL).

_passed(compile,DECL) :- _passed(solve,DECL), _label(LBL,DECL), engine(LBL,compile), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(ground,DECL) :- _passed(solve,DECL), _label(LBL,DECL), engine(LBL,ground), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(propagator,DECL) :- _passed(solve,DECL), _label(LBL,DECL), engine(LBL,propagator), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).

%_passed(ENGINE,bool_evaluate(LBL,E)) :- _passed(solve,bool_evaluate(LBL,E)), engine(LBL,ENGINE).
%_passed(ENGINE,ensure(LBL,E)) :- _passed(solve,ensure(LBL,E)), engine(LBL,ENGINE).
%_passed(ENGINE,evaluate(LBL,OP,ARGS)) :- _passed(solve,evaluate(LBL,OP,ARGS)), engine(LBL,ENGINE).
%_passed(ENGINE,variable_declare(LBL,X,D)) :- _passed(solve,variable_declare(LBL,X,D)), engine(LBL,ENGINE).
%_passed(ENGINE,variable_define(LBL,X,E)) :- _passed(solve,variable_define(LBL,X,E)), engine(LBL,ENGINE).
%_passed(ENGINE,variable_domain(LBL,X,E)) :- _passed(solve,variable_domain(LBL,X,E)), engine(LBL,ENGINE).
%_passed(ENGINE,set_assign(LBL,X,E)) :- _passed(solve,set_assign(LBL,X,E)), engine(LBL,ENGINE).
%_passed(ENGINE,set_baseDomain(LBL,X,E)) :- _passed(solve,set_baseDomain(LBL,X,E)), engine(LBL,ENGINE).
%_passed(ENGINE,multimap_assign(LBL,X,K,V)) :- _passed(solve,multimap_assign(LBL,X,K,V)), engine(LBL,ENGINE).
%_passed(ENGINE,optimize_maximizeSum(LBL,E,X,P)) :- _passed(solve,optimize_maximizeSum(LBL,E,X,P)), engine(LBL,ENGINE).
%_passed(ENGINE,optimize_precision(LBL,PREC,PRIO)) :- _passed(solve,optimize_precision(LBL,PREC,PRIO)), engine(LBL,ENGINE).

_passed(ENGINE,warning_forbid(LBL,W)) :- _passed(solve,warning_forbid(LBL,W)), _main_engine(ENGINE).
_passed(ENGINE,warning_ignore(LBL,W)) :- _passed(solve,warning_ignore(LBL,W)), _main_engine(ENGINE).
