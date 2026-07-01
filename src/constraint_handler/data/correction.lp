%%%%%%%%%%%%%%%%% expressions
_correction_expressionCorrected(PHASE,E) :- _phase_active(PHASE), _correction_expression(PHASE,E,N).
_correction_expressionOutput(PHASE,E,E) :- _phase_active(PHASE), _expression(sugar,E), not _correction_expressionCorrected(PHASE,E).
_correction_expressionOutput(PHASE,E,N) :-  _correction_expression(PHASE,E,N).

%%%%%%%%%%%%%%%%% numbers
_correction_numberCorrected(PHASE,E) :- _phase_active(PHASE), _correction_number(PHASE,E,N).
_correction_numberOutput(PHASE,E,E) :- _phase_active(PHASE), _number(sugar,E), not _correction_numberCorrected(PHASE,E).
_correction_numberOutput(PHASE,E,N) :- _phase_active(PHASE), _correction_number(PHASE,E,N).

%%%%%%%%%%%%%%%%% corrections
_correction_proposed(PHASE,LBL,bool_evaluate(E),bool_evaluate(NE)) :-
  _passed(sugar,LBL,bool_evaluate(E)),
  _correction_expressionOutput(PHASE,E,NE).
_correction_proposed(PHASE,LBL,ensure(E),ensure(NE)) :-
  _passed(sugar,LBL,ensure(E)),
  _correction_expressionOutput(PHASE,E,NE).
_correction_proposed(PHASE,LBL,evaluate(OP,ARGS),evaluate(NOP,NARGS)) :-
  _passed(sugar,LBL,evaluate(OP,ARGS)),
  _correction_expressionOutput(PHASE,operation(OP,ARGS),operation(NOP,NARGS)). % TODO: do better
_correction_proposed(PHASE,LBL,variable_define(X,E),variable_define(X,NE)) :-
  _passed(sugar,LBL,variable_define(X,E)),
  _correction_expressionOutput(PHASE,E,NE).
_correction_proposed(PHASE,LBL,variable_domain(X,E),variable_domain(X,NE)) :-
  _passed(sugar,LBL,variable_domain(X,E)),
  _correction_expressionOutput(PHASE,E,NE).
_correction_proposed(PHASE,LBL,set_assign(X,E),set_assign(X,NE)) :-
  _passed(sugar,LBL,set_assign(X,E)),
  _correction_expressionOutput(PHASE,E,NE).
_correction_proposed(PHASE,LBL,set_baseDomain(X,E),set_baseDomain(X,NE)) :-
  _passed(sugar,LBL,set_baseDomain(X,E)),
  _correction_expressionOutput(PHASE,E,NE).
_correction_proposed(PHASE,LBL,multimap_assign(X,K,B),multimap_assign(X,NK,NB)) :-
  _passed(sugar,LBL,multimap_assign(X,K,B)),
  _correction_expressionOutput(PHASE,K,NK), _correction_expressionOutput(PHASE,B,NB).
_correction_proposed(PHASE,LBL,optimize_component(E,PREC,ID,PRIO),optimize_component(NE,NREC,ID,NRIO)) :-
  _passed(sugar,LBL,optimize_component(E,PREC,ID,PRIO)),
  _correction_expressionOutput(PHASE,E,NE),
  _correction_expressionOutput(PHASE,PREC,NREC),
  _correction_numberOutput(PHASE,PRIO,NRIO).
_correction_proposed(PHASE,LBL,preference_holds(E,K),preference_holds(NE,NK)) :- _passed(sugar,LBL,preference_holds(E,K)),
  _correction_expressionOutput(PHASE,E,NE),
  _correction_numberOutput(PHASE,K,NK).


_correction(PHASE,LBL,D1,D2) :- _correction_proposed(PHASE,LBL,D1,D2), D1 != D2.


_passed(correction(PHASE,rem),LBL,DECL) :- _correction(PHASE,LBL,DECL,NECL).
_passed(correction(PHASE,rem),LBL,DECL) :- _correction(PHASE,LBL,DECL,NECL).
_passed(correction(PHASE,add),LBL,NECL) :- _correction(PHASE,LBL,DECL,NECL).

_warning(correction(PHASE),(),DECL) :- _correction(PHASE,LBL,DECL,NECL), #false: _passed(internal_declaration,LBL2,DECL).
