%%%%%%%%%%%%%%%%% _statement_query,
_statement_query(PRG,(PRG,()),STMT) :- _execution_declare(LBL,PRG,STMT,INS,OUTS).
_statement_query(PRG,SCOPE,STM1) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,STM2) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,THEN) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(PRG,SCOPE,ELSE) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).

%%%%%%%%%%%%%%%%% _statement_wellformed
_statement_wellformed(seq2(STM1,STM2)) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)), _statement_wellformed(STM1), _statement_wellformed(STM2).
_statement_wellformed(noop) :- _statement_query(PRG,SCOPE,noop).
_statement_wellformed(statement_python(STR)) :- _statement_query(PRG,SCOPE,statement_python(STR)), (string,_,_,_)=@pythonReify(STR).
_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_wellformed(THEN), true=@pythonIsExpr(EXPR), _statement_wellformed(ELSE).
_statement_wellformed(assign(X,EXPR)) :- _statement_query(PRG,SCOPE,assign(X,EXPR)), true=@pythonIsExpr(EXPR).
_statement_wellformed(assert(EXPR)) :- _statement_query(PRG,SCOPE,assert(EXPR)), true=@pythonIsExpr(EXPR).
%_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)), _expression_wellformed(EXPR), _statement_wellformed(THEN), _statement_wellformed(ELSE).
%_statement_wellformed(assign(X,EXPR)) :- _statement_query(PRG,SCOPE,assign(X,EXPR)), _expression_wellformed(EXPR).
%_statement_wellformed(assert(EXPR)) :- _statement_query(PRG,SCOPE,assert(EXPR)), _expression_wellformed(EXPR).



_warning(statement(syntaxError),PRG,STMT) :- _statement_query(PRG,SCOPE,STMT), not _statement_wellformed(STMT).
%%% TODO: use a python check so that it takes place before SSA without reordering the phases







_execution_declare(LBL,PRG,STMT,INS,OUTS) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)).%, engine(LBL,(compile;ground)).
_execution_input_var(PRG,X) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(INS).
_execution_outputVar(PRG,X,execution_output(PRG,X)) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(OUTS).





_statement_querySSA(LBL,PRG,(PRG,()),STMT) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), _statement_wellformed(STMT).

_statement_querySSA(LBL,PRG,(t,SCOPE),THEN) :- _statement_querySSA(LBL,PRG,SCOPE,if(E,THEN,ELSE)).
_statement_querySSA(LBL,PRG,(e,SCOPE),ELSE) :- _statement_querySSA(LBL,PRG,SCOPE,if(E,THEN,ELSE)).
_statement_querySSA(LBL,PRG,(l,SCOPE),STM1) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)).
_statement_querySSA(LBL,PRG,(r,SCOPE),STM2) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)).

_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,assert(E)).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,E)).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,if(E,THEN,ELSE)).
_expression_querySSA(PRG,SCOPE,D) :- _expression_querySSA(PRG,SCOPE,operation(O,ARGS)), D=@pythonListElements(ARGS).
_expression_querySSA(PRG,SCOPE,D) :- _expression_querySSA(PRG,SCOPE,E), _expression_isTuple(defaultArgs,E,N,ARGS), D=@pythonListElements(ARGS).
% TODO: tuple, set

_expression_sequenceHelper(defaultArgs,E) :- _expression_querySSA(PRG,SCOPE,E).

_statement_pythonVarsResult(PRG,SCOPE,R) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _main_solverIdentifiers(ID), R=@pythonStatementVariables(CODE,(),ID).
_warning(KIND,PRG,MSG) :- _statement_pythonVarsResult(PRG,SCOPE,error(KIND,MSG)).


%%%%% statement_changed
_statement_changed(STMT,X) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assign(X,EX).
_statement_changed(STMT,X) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_changed(STM1,X).
_statement_changed(STMT,X) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_changed(STM2,X).
_statement_changed(STMT,X) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_changed(THEN,X).
_statement_changed(STMT,X) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_changed(ELSE,X).
_statement_changed(STMT,X) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE), _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)).


%%%%% statement_context

_statement_context((PRG,()),X,variable(execution_input(PRG,X))) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(INS).


_statement_context((l,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_context(SCOPE,X,XS).
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_context(SCOPE,X,XS), _statement_latest((l,SCOPE),X,X2). % TODO: strange, double-check
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_latest((l,SCOPE),X,X2).
_statement_context((t,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(C,T,E)), _statement_context(SCOPE,X,XS).
_statement_context((e,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(C,T,E)), _statement_context(SCOPE,X,XS).


_expression_context(SCOPE,E,X,XS) :- _expression_querySSA(PRG,SCOPE,E), _statement_context(SCOPE,X,XS).
% TODO: handle lambda context


_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(PRG,SCOPE,E), E=val(T,V).
_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(PRG,SCOPE,E), E=bad.
_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(PRG,SCOPE,E), E=python(CODE).
_expression_contextualized(SCOPE,E,XS) :- _expression_querySSA(PRG,SCOPE,E), E=variable(X), _expression_context(SCOPE,E,X,XS).
%TODO other vars!
_statement_hasContext(SCOPE,X) :- _statement_context(SCOPE,X,XS).
_expression_contextualized(SCOPE,E,XS) :- _expression_querySSA(PRG,SCOPE,E), E=variable(X), not _statement_hasContext(SCOPE,X), XS=variable(execution_local(PRG,X)).
_expression_contextualizedListAux(SCOPE,E,N,()) :- _expression_querySSA(PRG,SCOPE,E), _length(defaultArgs,E,N).
_expression_contextualizedListAux(SCOPE,E,IDX,(DC,L)) :- _expression_querySSA(PRG,SCOPE,E), _expression_contextualizedListAux(SCOPE,E,IDX+1,L),
   _expression_index(defaultArgs,E,IDX,D), _expression_contextualized(SCOPE,D,DC).
_expression_contextualized(SCOPE,E,operation(O,L)) :- _expression_contextualizedListAux(SCOPE,E,0,L), E=operation(O,ARGS).
_expression_contextualized(SCOPE,E,@pythonReflect(function,(),L)) :- _expression_contextualizedListAux(SCOPE,E,0,L), _expression_isTuple(defaultArgs,E,N,ARGS).

% TODO: operators

%%%%% statement_condition
_statement_condition((PRG,()),()) :- _execution_declare(LBL,PRG,STMT,INS,OUTS).
_statement_condition((l,SCOPE),ES) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_condition(SCOPE,ES).
_statement_condition((r,SCOPE),ES) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_condition(SCOPE,ES).
_statement_condition((t,SCOPE),(E,ES)) :- _statement_querySSA(LBL,PRG,SCOPE,if(COND,THEN,ELSE)), _expression_contextualized(SCOPE,COND,E), _statement_condition(SCOPE,ES).
_statement_condition((e,SCOPE),(NE,ES)) :- _statement_querySSA(LBL,PRG,SCOPE,if(COND,THEN,ELSE)), _expression_contextualized(SCOPE,COND,E), _statement_condition(SCOPE,ES), NE=operation(lnot,(E,())).


%%%%% statement_latest
_statement_scoped(SCOPE,X,variable(loc(@pythonScopeToString(SCOPE,X)))) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)).
_statement_scoped(SCOPE,X,variable(loc(@pythonScopeToString(SCOPE,X)))) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed(if(EXPR,THEN,ELSE),X).
_statement_scoped(SCOPE,X,variable(loc(@pythonScopeToString(SCOPE,X)))) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
  _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)).

%_statement_scoped(SCOPE,X,variable(loc(SCOPE,X))) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)).
%_statement_scoped(SCOPE,X,variable(loc(SCOPE,X))) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed(if(EXPR,THEN,ELSE),X).
%_statement_scoped(SCOPE,X,variable(loc(SCOPE,X))) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
%  _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)).


_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)), _statement_scoped(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,assign(V,EX)), _statement_context(SCOPE,X,XS), V!=X.
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,assert(E)), _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,noop), _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)), _statement_latest((r,SCOPE),X,XS).
%_statement_context((r,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)), _statement_latest((r,SCOPE),X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed(STMT,X), _statement_scoped(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_context(SCOPE,X,XS), not _statement_changed(if(EXPR,THEN,ELSE),X).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)), _statement_scoped(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _statement_context(SCOPE,X,XS), #false : _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)).






_statement_indexedVar(SCOPE,IDX,X) :- _statement_context(SCOPE,X,XS), true=@pythonIsString(X), IDX=#count { Y: _statement_context(SCOPE,Y,YS), true=@pythonIsString(Y), Y<X }.
_statement_countVars(SCOPE,N) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), N=#count { X: _statement_context(SCOPE,X,XS), true=@pythonIsString(X) }.

_statement_pythonInputMapAux(SCOPE,N,()) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _statement_countVars(SCOPE,N).
_statement_pythonInputMapAux(SCOPE,IDX,((val(string,Y),YS),VARS)) :- _statement_pythonInputMapAux(SCOPE,IDX+1,VARS), _statement_indexedVar(SCOPE,IDX,Y), _statement_context(SCOPE,Y,YS).
_statement_pythonInputMap(SCOPE,VARS) :- _statement_pythonInputMapAux(SCOPE,0,VARS).








%%% SSA output
_statement_definedLatest(SCOPE,X) :- _statement_latest(SCOPE,X,XE).
_statement_introduce(LBL,XS,XI) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((t,SCOPE),X,XT), _statement_latest((e,SCOPE),X,XE), _statement_latest(SCOPE,X,variable(XS)),
XI=operation(ite,(COND,(XT,(XE,())))), _statement_changed(STMT,X).
_statement_introduce(LBL,XS,XI) :- _statement_querySSA(LBL,PRG,SCOPE,if(C,THEN,ELSE)), _expression_contextualized(SCOPE,C,COND), _statement_latest((t,SCOPE),X,XT), not _statement_definedLatest((e,SCOPE),X), _statement_latest(SCOPE,X,variable(XS)), XI=operation(ite,(COND,(XT,(val(none,none),())))).
_statement_introduce(LBL,XS,XI) :- _statement_querySSA(LBL,PRG,SCOPE,if(C,THEN,ELSE)), _expression_contextualized(SCOPE,C,COND), _statement_latest((e,SCOPE),X,XE), not _statement_definedLatest((t,SCOPE),X), _statement_latest(SCOPE,X,variable(XS)),
XI=operation(ite,(COND,(val(none,none),(XE,())))).
_statement_introduce(LBL,XS,EX) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,E)), _expression_contextualized(SCOPE,E,EX), _statement_latest(SCOPE,X,variable(XS)).
_statement_ensure(LBL,ASSR) :- _statement_querySSA(LBL,PRG,SCOPE,assert(E)),
  _expression_contextualized(SCOPE,E,EX),
  _statement_condition(SCOPE,ES),
  CONJ=operation(conj,ES),
  ASSR=operation(limp,(CONJ,(EX,()))),
  _execution_isRunning(PRG).


_statement_introduce(LBL,XS,EX) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,E)), _expression_contextualized(SCOPE,E,EX),_statement_latest(SCOPE,X,variable(XS)).
_statement_introduce(LBL,XS,operation(pythonExtract(CODE,X),VARS)) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
  _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)), _statement_pythonInputMap(SCOPE,VARS),_statement_latest(SCOPE,X,variable(XS)).
_statement_ensure(LBL,operation(pythonExtract(CODE,"__succeeds"),VARS)) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
  _statement_pythonInputMap(SCOPE,VARS),
  _execution_isRunning(PRG).

_statement_introduce(LBL,execution_local(PRG,X),variable(execution_input(PRG,X))) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), _execution_input_var(PRG,X).

%%% TODO: add bad / error handling
_execution_ou_proj(PRG,X) :- _statement_latest((PRG,()),X,EX).

_execution_isRunning(PRG) :- _execution_declare(LBL1,PRG,STMT,INS,OUTS), _passed(defaultArgs,execution_run(LBL,PRG)).

_statement_introduce(LBL,EX,V) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), _statement_latest((PRG,()),X,V), _execution_isRunning(PRG).
_statement_introduce(LBL,EX,val(none,none)) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), #false : _execution_ou_proj(PRG,X), _execution_isRunning(PRG).

_passed(sugar,variable_define(LBL,X,E)) :- _statement_introduce(LBL,X,E).
_passed(sugar,variable_declare(LBL,X,definition)) :- _statement_introduce(LBL,X,E).
_passed(sugar,ensure(LBL,E)) :- _statement_ensure(LBL,E).