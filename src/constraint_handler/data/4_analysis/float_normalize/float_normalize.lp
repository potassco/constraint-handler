%%%%%%%%%%%%%%%%% _corrections
_float_normalizeQuery(EXPR) :- _phase_active(float_normalize), _expression(sugar,LBL,DECL,EXPR).
_correction_expression(float_normalize,EXPR,NXPR) :- _float_normalizeQuery(EXPR), NXPR=@pythonNormalExpr(EXPR), EXPR != NXPR.
