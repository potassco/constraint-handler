%%%%%%%%%%%%%%%%% _expression_toplevel
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,bool_evaluate(E)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,ensure(E)).
_expression_toplevel(sugar,LBL,operation(OP,ARGS)) :- _passed(sugar,LBL,evaluate(OP,ARGS)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,variable_define(X,E)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,variable_domain(X,E)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,set_assign(X,E)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,set_baseDomain(X,E)).
_expression_toplevel(sugar,LBL,(K;B)) :- _passed(sugar,LBL,multimap_assign(X,K,B)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,optimize_maximizeSum(E,X,P)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,optimize_precision(E,PRIO)).
_expression_toplevel(sugar,LBL,E) :- _passed(sugar,LBL,preference_holds(E,K)).

%%%%%%%%%%%%%%%%% _expression_normal
_float_normalizeQuery(EXPR) :- _phase_active(float_normalize), _expression_toplevel(sugar,LBL,EXPR).
_float_normal(EXPR,NXPR) :- _float_normalizeQuery(EXPR), NXPR=@pythonNormalExpr(EXPR), EXPR != NXPR.
_float_normalized(EXPR) :- _float_normal(EXPR,NXPR).

%%%%%%%%%%%%%%%%% corrections
_float_normalizeDecl(LBL,bool_evaluate(E),bool_evaluate(NE)) :- _passed(sugar,LBL,bool_evaluate(E)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,ensure(E),ensure(NE)) :- _passed(sugar,LBL,ensure(E)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,evaluate(OP,ARGS),evaluate(NOP,NARGS)) :- _passed(sugar,LBL,evaluate(OP,ARGS)),
  _float_normal(operation(OP,ARGS),operation(NOP,NARGS)).
_float_normalizeDecl(LBL,variable_define(X,E),variable_define(X,NE)) :- _passed(sugar,LBL,variable_define(X,E)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,variable_domain(X,E),variable_domain(X,NE)) :- _passed(sugar,LBL,variable_domain(X,E)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,set_assign(X,E),set_assign(X,NE)) :- _passed(sugar,LBL,set_assign(X,E)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,set_baseDomain(X,E),set_baseDomain(X,NE)) :- _passed(sugar,LBL,set_baseDomain(X,E)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,multimap_assign(X,K,B),multimap_assign(X,NK,NB)) :- _passed(sugar,LBL,multimap_assign(X,K,B)),
  _float_normal(K,NK), _float_normal(B,NB).
_float_normalizeDecl(LBL,multimap_assign(X,K,B),multimap_assign(X,NK,B)) :- _passed(sugar,LBL,multimap_assign(X,K,B)),
  _float_normal(K,NK), not _float_normalized(B).
_float_normalizeDecl(LBL,multimap_assign(X,K,B),multimap_assign(X,K,NB)) :- _passed(sugar,LBL,multimap_assign(X,K,B)),
  not _float_normalized(K), _float_normal(B,NB).
_float_normalizeDecl(LBL,optimize_maximizeSum(E,X,P),optimize_maximizeSum(NE,X,P)) :- _passed(sugar,LBL,optimize_maximizeSum(E,X,P)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,optimize_precision(E,PRIO),optimize_precision(NE,PRIO)) :- _passed(sugar,LBL,optimize_precision(E,PRIO)),
  _float_normal(E,NE).
_float_normalizeDecl(LBL,preference_holds(E,K),preference_holds(NE,K)) :- _passed(sugar,LBL,preference_holds(E,K)),
  _float_normal(E,NE).


_passed(correction(float_normalize,rem),LBL,DECL) :- _float_normalizeDecl(LBL,DECL,NECL).
_passed(correction(float_normalize,add),LBL,NECL) :- _float_normalizeDecl(LBL,DECL,NECL).

_warning(expression(normalizedFloat),(),DECL) :- _float_normalizeDecl(LBL,DECL,NECL).
