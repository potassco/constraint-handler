_execution_declare(LBL,PRG,STMT,INS,OUTS) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)).
_execution_inputVar(LBL,PRG,X,execution_input(PRG,X)) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), X=@pythonListElements(INS).
_execution_outputVar(LBL,PRG,X,execution_output(PRG,X)) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), X=@pythonListElements(OUTS).





_statement_querySSA(LBL,PRG,(PRG,()),STMT) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)).

_statement_querySSA(LBL,PRG,(t,SCOPE),THEN) :- _statement_querySSA(LBL,PRG,SCOPE,if(E,THEN,ELSE)).
_statement_querySSA(LBL,PRG,(e,SCOPE),ELSE) :- _statement_querySSA(LBL,PRG,SCOPE,if(E,THEN,ELSE)).
_statement_querySSA(LBL,PRG,(l,SCOPE),STM1) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)).
_statement_querySSA(LBL,PRG,(r,SCOPE),STM2) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)).

_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,assert(E)).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,E)).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,if(E,THEN,ELSE)).
_expression_querySSA(PRG,SCOPE,D) :- _expression_querySSA(PRG,SCOPE,E), _expression_operationIndex(defaultArgs,E,IDX,D).
_expression_querySSA(PRG,SCOPE,D) :- _expression_querySSA(PRG,SCOPE,E), _expression_tupleIndex(defaultArgs,E,IDX,D).
% TODO: tuple, set

%_expression_sequenceHelper(defaultArgs,E) :- _expression_querySSA(PRG,SCOPE,E).
_expression(defaultArgs,E) :- _expression_querySSA(PRG,SCOPE,E).

_statement_pythonVarsResult(PRG,SCOPE,R) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _main_solverIdentifiers(ID), R=@pythonStatementVariables(CODE,(),ID).
_warning(KIND,PRG,MSG) :- _statement_pythonVarsResult(PRG,SCOPE,error(KIND,MSG)).


%%%%% statement_changed
_statement_changed(assign(X,EX),X) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)).
_statement_changed(seq2(STM1,STM2),X) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)), _statement_changed((STM1;STM2),X).
_statement_changed(if(EXPR,THEN,ELSE),X) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed((THEN;ELSE),X).
_statement_changed(statement_python(CODE),X) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _statement_pythonVarsResult(PRG,SCOPE,valid(X)).


%%%%% statement_context

_statement_context((PRG,()),X,variable(execution_input(PRG,X))) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), X=@pythonListElements(INS).


_statement_context((l,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_context(SCOPE,X,XS).
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_context(SCOPE,X,XS), _statement_latest((l,SCOPE),X,X2). % TODO: strange, double-check
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_latest((l,SCOPE),X,X2).
_statement_context((t,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(C,T,E)), _statement_context(SCOPE,X,XS).
_statement_context((e,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(C,T,E)), _statement_context(SCOPE,X,XS).


_expression_context(SCOPE,E,X,XS) :- _expression_querySSA(PRG,SCOPE,E), _statement_context(SCOPE,X,XS).
% TODO: handle lambda context


_expression_contextualized(SCOPE,val(T,V),val(T,V)) :- _expression_querySSA(PRG,SCOPE,val(T,V)).
_expression_contextualized(SCOPE,bad,bad) :- _expression_querySSA(PRG,SCOPE,bad).
_expression_contextualized(SCOPE,python(CODE),python(CODE)) :- _expression_querySSA(PRG,SCOPE,python(CODE)).
_expression_contextualized(SCOPE,variable(X),XS) :- _expression_querySSA(PRG,SCOPE,variable(X)), _expression_context(SCOPE,variable(X),X,XS).
%TODO other vars!
_statement_hasContext(SCOPE,X) :- _statement_context(SCOPE,X,XS).
_expression_contextualized(SCOPE,variable(X),variable(execution_input(PRG,X))) :- _expression_querySSA(PRG,SCOPE,variable(X)), not _statement_hasContext(SCOPE,X).

_expression_contextualizedOperationAux(SCOPE,E,N,()) :- _expression_querySSA(PRG,SCOPE,E), _expression_operationLength(defaultArgs,E,N).
_expression_contextualizedOperationAux(SCOPE,E,IDX,(DC,L)) :- _expression_querySSA(PRG,SCOPE,E), _expression_contextualizedOperationAux(SCOPE,E,IDX+1,L),
    _expression_operationIndex(defaultArgs,E,IDX,D), _expression_contextualized(SCOPE,D,DC).
_expression_contextualized(SCOPE,operation(O,ARGS),operation(O,L)) :- _expression_contextualizedOperationAux(SCOPE,operation(O,ARGS),0,L).

_expression_contextualizedTupleAux(SCOPE,E,N,()) :- _expression_querySSA(PRG,SCOPE,E), _expression_tupleLength(defaultArgs,E,N).
_expression_contextualizedTupleAux(SCOPE,E,IDX,(DC,L)) :- _expression_querySSA(PRG,SCOPE,E),
    _expression_contextualizedTupleAux(SCOPE,E,IDX+1,L),
    _expression_tupleIndex(defaultArgs,E,IDX,D), _expression_contextualized(SCOPE,D,DC).
_expression_contextualized(SCOPE,E,@pythonReflect(function,(),L)) :- _expression_contextualizedTupleAux(SCOPE,E,0,L).

% TODO: operators

%%%%% statement_condition
_statement_condition((PRG,()),()) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)).
_statement_condition((l,SCOPE),ES) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_condition(SCOPE,ES).
_statement_condition((r,SCOPE),ES) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(S1,S2)), _statement_condition(SCOPE,ES).
_statement_condition((t,SCOPE),(E,ES)) :- _statement_querySSA(LBL,PRG,SCOPE,if(COND,THEN,ELSE)), _expression_contextualized(SCOPE,COND,E), _statement_condition(SCOPE,ES).
_statement_condition((e,SCOPE),(NE,ES)) :- _statement_querySSA(LBL,PRG,SCOPE,if(COND,THEN,ELSE)), _expression_contextualized(SCOPE,COND,E), _statement_condition(SCOPE,ES), NE=operation(lnot,(E,())).


%%%%% statement_latest
_statement_scoped(SCOPE,X,variable(loc(@pythonScopeToString(SCOPE,X)))) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)).
_statement_scoped(SCOPE,X,variable(loc(@pythonScopeToString(SCOPE,X)))) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed(if(EXPR,THEN,ELSE),X).
_statement_scoped(SCOPE,X,variable(loc(@pythonScopeToString(SCOPE,X)))) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
  _statement_pythonVarsResult(PRG,SCOPE,valid(X)).

%_statement_scoped(SCOPE,X,variable(loc(SCOPE,X))) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)).
%_statement_scoped(SCOPE,X,variable(loc(SCOPE,X))) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed(if(EXPR,THEN,ELSE),X).
%_statement_scoped(SCOPE,X,variable(loc(SCOPE,X))) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
%  _statement_pythonVarsResult(PRG,SCOPE,valid(X)).


_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,assign(X,EX)), _statement_scoped(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,assign(V,EX)), _statement_context(SCOPE,X,XS), V!=X.
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,assert(E)), _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,noop), _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)), _statement_latest((r,SCOPE),X,XS).
%_statement_context((r,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,seq2(STM1,STM2)), _statement_latest((r,SCOPE),X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_changed(STMT,X), _statement_scoped(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_context(SCOPE,X,XS), not _statement_changed(if(EXPR,THEN,ELSE),X).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _statement_pythonVarsResult(PRG,SCOPE,valid(X)), _statement_scoped(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)), _statement_context(SCOPE,X,XS), #false : _statement_pythonVarsResult(PRG,SCOPE,valid(X)).






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
  _statement_pythonVarsResult(PRG,SCOPE,valid(X)), _statement_pythonInputMap(SCOPE,VARS),_statement_latest(SCOPE,X,variable(XS)).
_statement_ensure(LBL,ASSR) :- _statement_querySSA(LBL,PRG,SCOPE,statement_python(CODE)),
  _statement_pythonInputMap(SCOPE,VARS),
  _statement_condition(SCOPE,ES),
  CONJ=operation(conj,ES),
  SUCCEEDS=operation(pythonExtract(CODE,"__succeeds"),VARS),
  ASSR=operation(limp,(CONJ,(SUCCEEDS,()))),
  _execution_isRunning(PRG).

%%% TODO: add bad / error handling
_execution_ou_proj(PRG,X) :- _statement_latest((PRG,()),X,EX).

_execution_isRunning(PRG) :- _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), _passed(defaultArgs,LBL1,execution_run(PRG)).

_statement_introduce(LBL,EX,V) :- _execution_outputVar(LBL,PRG,X,EX), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), _statement_latest((PRG,()),X,V), _execution_isRunning(PRG).
_statement_introduce(LBL,EX,val(none,none)) :- _execution_outputVar(LBL,PRG,X,EX), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), not _execution_ou_proj(PRG,X).
_statement_introduce(LBL,EX,val(none,none)) :- _execution_outputVar(LBL,PRG,X,EX), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)), not _execution_isRunning(PRG).

_passed(ssa,LBL,variable_define(X,E)) :- _statement_introduce(LBL,X,E).
_passed(ssa,LBL,variable_declare(X,definition)) :- _statement_introduce(LBL,X,E).
_passed(ssa,LBL,ensure(E)) :- _statement_ensure(LBL,E).
_variable(ssa,EX) :- _execution_inputVar(LBL,PRG,X,EX).
