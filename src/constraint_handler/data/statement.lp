%%%%%%%%%%%%%%%%% _statement_query,
_statement_query(PRG,(PRG,()),STMT) :- _execution_declare(LBL,PRG,STMT,INS,OUTS).
_statement_query(PRG,SCOPE,STM1) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,STM2) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,THEN) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(PRG,SCOPE,ELSE) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(PRG,SCOPE,BODY) :- _statement_query(PRG,SCOPE,while(MAX,EXPR,BODY)).

%%%%%%%%%%%%%%%%% _statement_wellformed
_statement_wellformed(seq2(STM1,STM2)) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)), _statement_wellformed(STM1), _statement_wellformed(STM2).
_statement_wellformed(noop) :- _statement_query(PRG,SCOPE,noop).
_statement_wellformed(statement_python(STR)) :- _statement_query(PRG,SCOPE,statement_python(STR)), (string,_,_,_)=@pythonReify(STR).
_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_wellformed(THEN), _statement_wellformed(ELSE).
_statement_wellformed(assign(X,EXPR)) :- _statement_query(PRG,SCOPE,assign(X,EXPR)).
_statement_wellformed(assert(EXPR)) :- _statement_query(PRG,SCOPE,assert(EXPR)).
_statement_wellformed(while(MAX,EXPR,BODY)) :- _statement_query(PRG,SCOPE,while(MAX,EXPR,BODY)), _statement_wellformed(BODY).
%_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)), _expression_wellformed(EXPR), _statement_wellformed(THEN), _statement_wellformed(ELSE).
%_statement_wellformed(assign(X,EXPR)) :- _statement_query(PRG,SCOPE,assign(X,EXPR)), _expression_wellformed(EXPR).
%_statement_wellformed(assert(EXPR)) :- _statement_query(PRG,SCOPE,assert(EXPR)), _expression_wellformed(EXPR).
%_statement_wellformed(while(MAX,EXPR,BODY)) :- _statement_query(PRG,SCOPE,while(MAX,EXPR,BODY)), _expression_wellformed(EXPR), _statement_wellformed(BODY).


_expression_query(sugar,PRG,EXPR) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_expression_query(sugar,PRG,EXPR) :- _statement_query(PRG,SCOPE,assign(X,EXPR)).
_expression_query(sugar,PRG,EXPR) :- _statement_query(PRG,SCOPE,assert(EXPR)).
_expression_query(sugar,PRG,EXPR) :- _statement_query(PRG,SCOPE,while(MAX,EXPR,BODY)).

_warning(statement(syntaxError),PRG,STMT) :- _statement_query(PRG,SCOPE,STMT), not _statement_wellformed(STMT).
%%% TODO: use a python check so that it takes place before SSA without reordering the phases







_execution_declare(LBL,PRG,STMT,INS,OUTS) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)).%, engine(LBL,(compile;ground)).
_execution_input_var(PRG,X) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(INS).
_execution_outputVar(PRG,X,execution_output(PRG,X)) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(OUTS).





_statement_querySSA(LBL,PRG,(PRG,()),STMT) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), _statement_wellformed(STMT).

_statement_querySSA(LBL,PRG,(t,SCOPE),THEN) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(E,THEN,ELSE).
_statement_querySSA(LBL,PRG,(e,SCOPE),ELSE) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(E,THEN,ELSE).
_statement_querySSA(LBL,PRG,(l,SCOPE),STM1) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(STM1,STM2).
_statement_querySSA(LBL,PRG,(r,SCOPE),STM2) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(STM1,STM2).

_expression_sequenceHelper(defaultArgs,E) :- _expression_querySSA(PRG,SCOPE,E).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assert(E).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assign(X,E).
_expression_querySSA(PRG,SCOPE,E) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(E,THEN,ELSE).
_expression_querySSA(PRG,SCOPE,F) :- _expression_querySSA(PRG,SCOPE,E), E=operation(O,ARGS), F=@pythonListElements(ARGS).
_expression_querySSA(PRG,SCOPE,F) :- _expression_querySSA(PRG,SCOPE,E), _expression_isTuple(defaultArgs,E,N,ARGS), F=@pythonListElements(ARGS).
% TODO: tuple, set


_statement_pythonVarsResult(PRG,SCOPE,R) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE), _main_solverIdentifier(ID), R=@pythonStatementVariables(CODE,(),ID).
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


_statement_context((l,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=seq2(S1,S2).
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=seq2(S1,S2), _statement_latest((l,SCOPE),X,X2).
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(S1,S2), _statement_latest((l,SCOPE),X,X2).
_statement_context((t,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=if(C,T,E).
_statement_context((e,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=if(C,T,E).
%TODO statement_python


_expression_sequenceHelper(defaultArgs,ARGS) :- _expression_querySSA(PRG,SCOPE,E), E=operation(O,ARGS).
_expression_sequenceHelper(defaultArgs,E) :- _expression_querySSA(PRG,SCOPE,E).

% TODO: can be made faster by defining subexpression/2.?
_expression_context(SCOPE,E,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=assign(V,E).
_expression_context(SCOPE,E,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=assert(E).
_expression_context(SCOPE,C,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=if(C,T,E).
_expression_context(SCOPE,D,X,XS) :- _expression_context(SCOPE,E,X,XS), E=operation(O,L), D=@pythonListElements(L).
_expression_context(SCOPE,D,X,XS) :- _expression_context(SCOPE,E,X,XS), D=@pythonTupleElements(E).
_expression_context(SCOPE,D,X,XS) :- _expression_context(SCOPE,E,X,XS), E=lambda(ARGS,D), #false: X=@pythonListElements(ARGS).

_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(PRG,SCOPE,E), E=val(T,V).
_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(PRG,SCOPE,E), E=bad.
_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(PRG,SCOPE,E), E=python(CODE).
_expression_contextualized(SCOPE,E,XS) :- _expression_querySSA(PRG,SCOPE,E), E=variable(X), _expression_context(SCOPE,E,X,XS).
%TODO other vars!
_statement_hasContext(SCOPE,X) :- _statement_context(SCOPE,X,XS).
_expression_contextualized(SCOPE,E,XS) :- _expression_querySSA(PRG,SCOPE,E), E=variable(X), not _statement_hasContext(SCOPE,X), XS=variable(execution_local(PRG,X)).
_expression_contextualizedListAux(SCOPE,E,ARGS,N,()) :- _expression_querySSA(PRG,SCOPE,E), E=operation(O,ARGS), _length(defaultArgs,ARGS,N).
_expression_contextualizedListAux(SCOPE,E,ARGS,IDX,(DC,L)) :- _expression_contextualizedListAux(SCOPE,E,ARGS,IDX+1,L),
   _expression_index(defaultArgs,ARGS,IDX,D), _expression_contextualized(SCOPE,D,DC).
_expression_contextualized(SCOPE,E,operation(O,L)) :- _expression_contextualizedListAux(SCOPE,E,ARGS,0,L), E=operation(O,ARGS).
% TODO: operators

_expression_contextualizedListAux(SCOPE,E,ARGS,N,()) :- _expression_querySSA(PRG,SCOPE,E), _expression_isTuple(defaultArgs,E,N,ARGS).
_expression_contextualized(SCOPE,E,@pythonReflect(function,(),L)) :- _expression_contextualizedListAux(SCOPE,E,ARGS,0,L), _expression_isTuple(defaultArgs,E,N,ARGS).


%%%%% statement_latest

_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assign(X,EX), XS=variable(loc(@pythonScopeToString(SCOPE,X))).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assign(V,EX), _statement_context(SCOPE,X,XS), V!=X.
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assert(E), _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=noop, _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_latest((r,SCOPE),X,XS).
%_statement_context((r,SCOPE),X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_latest((r,SCOPE),X,XS).
_statement_latest(SCOPE,X,XE) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_changed(STMT,X), XE=variable(loc(@pythonScopeToString(SCOPE,X))).
_statement_latest(SCOPE,X,XE) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_context(SCOPE,X,XE), not _statement_changed(STMT,X).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE), _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)), XS=variable(loc(@pythonScopeToString(SCOPE,X))).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE), _statement_context(SCOPE,X,XS), #false : _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)).






%_execution_varResult(PRG,R) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), R=@pythonEnumerateExecutionVariables(STMT,INS).
%_execution_indexedVar(PRG,IDX,X) :- _execution_varResult(PRG,(IDX,X)).
%_execution_countVars(PRG,N) :- _execution_varResult(PRG,length(N)).
%_statement_indexedVarAux(SCOPE,0,0) :- _statement_querySSA(LBL,PRG,SCOPE,STMT).
%_statement_indexedVarAux(SCOPE,PX+1,SX+1) :- _statement_indexedVarAux(SCOPE,PX,SX), _execution_indexedVar(PRG,PX,X), _statement_context(SCOPE,X,XS), true=@pythonIsString(X).
%_statement_hasContext(SCOPE,X) :- _statement_context(SCOPE,X,XS).
%_statement_indexedVarAux(SCOPE,PX+1,SX) :- _statement_indexedVarAux(SCOPE,PX,SX), _execution_indexedVar(PRG,PX,X), #false: _statement_context(SCOPE,X,XS), true=@pythonIsString(X).

%_statement_indexedVar(SCOPE,SX,X) :- _statement_indexedVarAux(SCOPE,PX,SX), _execution_indexedVar(PRG,PX,X), _statement_context(SCOPE,X,XS), true=@pythonIsString(X).
%_statement_countVars(SCOPE,SX) :- _statement_indexedVarAux(SCOPE,N,SX), _execution_countVars(PRG,N).

_statement_indexedVar(SCOPE,IDX,X) :- _statement_context(SCOPE,X,XS), true=@pythonIsString(X), IDX=#count { Y: _statement_context(SCOPE,Y,YS), true=@pythonIsString(Y), Y<X }.
_statement_countVars(SCOPE,N) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), N=#count { X: _statement_context(SCOPE,X,XS), true=@pythonIsString(X) }.

_statement_pythonInputMapAux(SCOPE,N,()) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE), _statement_countVars(SCOPE,N).
_statement_pythonInputMapAux(SCOPE,IDX,((val(string,Y),YS),VARS)) :- _statement_pythonInputMapAux(SCOPE,IDX+1,VARS), _statement_indexedVar(SCOPE,IDX,Y), _statement_context(SCOPE,Y,YS).
_statement_pythonInputMap(SCOPE,VARS) :- _statement_pythonInputMapAux(SCOPE,0,VARS).








%%% SSA output
_statement_definedLatest(SCOPE,X) :- _statement_latest(SCOPE,X,XE).
_passed(sugar,variable_define(LBL,XS,XI)) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((t,SCOPE),X,XT), _statement_latest((e,SCOPE),X,XE),_statement_latest(SCOPE,X,variable(XS)),
XI=operation(ite,(COND,(XT,(XE,())))).
_passed(sugar,variable_define(LBL,XS,XI)) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((t,SCOPE),X,XT), not _statement_definedLatest((e,SCOPE),X),_statement_latest(SCOPE,X,variable(XS)), XI=operation(ite,(COND,(XT,(val(none,none),())))).
_passed(sugar,variable_define(LBL,XS,XI)) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((e,SCOPE),X,XE), not _statement_definedLatest((t,SCOPE),X), _statement_latest(SCOPE,X,variable(XS)),
XI=operation(ite,(COND,(val(none,none),(XE,())))).
_passed(sugar,variable_define(LBL,XS,EX)) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assign(X,E), _expression_contextualized(SCOPE,E,EX),_statement_latest(SCOPE,X,variable(XS)).
_passed(sugar,ensure(LBL,EX)) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assert(E), _expression_contextualized(SCOPE,E,EX),
  _execution_isRunning(PRG).

_passed(sugar,variable_define(LBL,XS,EX)) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=assign(X,E), _expression_contextualized(SCOPE,E,EX),_statement_latest(SCOPE,X,variable(XS)).
_passed(sugar,variable_define(LBL,XS,operation(pythonExtract(CODE,X),VARS))) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE),
  _statement_pythonVarsResult(PRG,SCOPE,(X,TYPE)), _statement_pythonInputMap(SCOPE,VARS),_statement_latest(SCOPE,X,variable(XS)).
_passed(sugar,ensure(LBL,operation(pythonExtract(CODE,"__succeeds"),VARS))) :- _statement_querySSA(LBL,PRG,SCOPE,STMT), STMT=statement_python(CODE),
  _statement_pythonInputMap(SCOPE,VARS),
  _execution_isRunning(PRG).

_passed(sugar,variable_define(_internal,execution_local(PRG,X),variable(execution_input(PRG,X)))) :- _execution_input_var(PRG,X).

%%% TODO: add bad / error handling
_execution_ou_proj(PRG,X) :- _statement_latest((PRG,()),X,EX).

_execution_isRunning(PRG) :- _execution_declare(LBL1,PRG,STMT,INS,OUTS), _passed(defaultArgs,execution_run(LBL,PRG)).

_passed(sugar,variable_define(LBL,EX,V)) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), _statement_latest((PRG,()),X,V), _execution_isRunning(PRG).
_passed(sugar,variable_define(LBL,EX,val(none,none))) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), #false : _execution_ou_proj(PRG,X), _execution_isRunning(PRG).