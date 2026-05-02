%%%%%%%%%%%%%%%%% _statement_query,
_statement_query((NAME,()),STMT) :- _passed(defaultArgs,execution_declare(CNAME,NAME,STMT,INS,OUTS)).
_statement_query(SCOPE,STM1) :- _statement_query(SCOPE,seq2(STM1,STM2)).
_statement_query(SCOPE,STM2) :- _statement_query(SCOPE,seq2(STM1,STM2)).
_statement_query(SCOPE,THEN) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(SCOPE,ELSE) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(SCOPE,BODY) :- _statement_query(SCOPE,while(MAX,EXPR,BODY)).

%%%%%%%%%%%%%%%%% _statement_wellformed
_statement_wellformed(seq2(STM1,STM2)) :- _statement_query(SCOPE,seq2(STM1,STM2)), _statement_wellformed(STM1), _statement_wellformed(STM2).
_statement_wellformed(noop) :- _statement_query(SCOPE,noop).
_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)), _expression_wellformed(EXPR), _statement_wellformed(THEN), _statement_wellformed(ELSE).
_statement_wellformed(assign(X,EXPR)) :- _statement_query(SCOPE,assign(X,EXPR)), _expression_wellformed(EXPR).
_statement_wellformed(assert(EXPR)) :- _statement_query(SCOPE,assert(EXPR)), _expression_wellformed(EXPR).
_statement_wellformed(statement_python(STR)) :- _statement_query(SCOPE,statement_python(STR)), (string,_,_,_)=@pythonReify(STR).
_statement_wellformed(while(MAX,EXPR,BODY)) :- _statement_query(SCOPE,while(MAX,EXPR,BODY)), _expression_wellformed(EXPR), _statement_wellformed(BODY).

_warning(statement(syntaxError),SCOPE,STMT) :- _statement_query(SCOPE,STMT), not _statement_wellformed(STMT).







%*
_execution_declare(LBL,PRG,STMT,INS,OUTS) :- _passed(sugar,execution_declare(LBL,PRG,STMT,INS,OUTS)), engine(LBL,(compile;ground)).
_execution_input_var(NAME,X) :- _execution_declare(LBL,NAME,STMT,INS,OUTS), X=@pythonListElements(INS).
_execution_outputVar(PRG,X,execution_output(PRG,X)) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(OUTS).
_execution_isRunning(PRG) :- _execution_declare(LBL1,PRG,STMT,INS,OUTS), _passed(sugar,execution_run(LBL,PRG)), engine(LBL,(compile;ground)).

_execution_ou_proj(PRG,X) :- _statement_latest((PRG,()),X,EX).



_statement_querySSA((PRG,()),STMT) :- _execution_declare(LBL,PRG,STMT,INS,OUTS).

_statement_querySSA((t,SCOPE),THEN) :- _statement_querySSA(SCOPE,STMT), STMT=if(E,THEN,ELSE).
_statement_querySSA((e,SCOPE),ELSE) :- _statement_querySSA(SCOPE,STMT), STMT=if(E,THEN,ELSE).
_statement_querySSA((l,SCOPE),STM1) :- _statement_querySSA(SCOPE,STMT), STMT=seq2(STM1,STM2).
_statement_querySSA((r,SCOPE),STM2) :- _statement_querySSA(SCOPE,STMT), STMT=seq2(STM1,STM2).

_expression_querySSA(SCOPE,E) :- _statement_querySSA(SCOPE,STMT), STMT=assert(E).
_expression_querySSA(SCOPE,E) :- _statement_querySSA(SCOPE,STMT), STMT=assign(X,E).
_expression_querySSA(SCOPE,E) :- _statement_querySSA(SCOPE,STMT), STMT=if(E,THEN,ELSE).
_expression_querySSA(SCOPE,F) :- _expression_querySSA(SCOPE,E), E=operation(O,ARGS), F=@pythonListElements(ARGS).
_expression_querySSA(SCOPE,F) :- _expression_querySSA(SCOPE,E), _expression_isTuple(E,N,ARGS), F=@pythonListElements(ARGS).
% TODO: tuple, set

_statement_pythonVarsResult(CODE,R) :- _statement_querySSA(SCOPE,STMT), STMT=statement_python(CODE), IN_TYPES=(), _main_solverIdentifier(ID), R=@pythonStatementVariables(CODE,IN_TYPES,ID).



_statement_changed(STMT,X) :- _statement_querySSA(SCOPE,STMT), STMT=assign(X,EX).
_statement_changed(STMT,X) :- _statement_querySSA(SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_changed(STM1,X).
_statement_changed(STMT,X) :- _statement_querySSA(SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_changed(STM2,X).
_statement_changed(STMT,X) :- _statement_querySSA(SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_changed(THEN,X).
_statement_changed(STMT,X) :- _statement_querySSA(SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_changed(ELSE,X).
_statement_changed(STMT,X) :- _statement_querySSA(SCOPE,STMT), STMT=statement_python(CODE), _statement_pythonVarsResult(CODE,(X,TYPES)).


_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=assign(X,EX), XS=variable(loc(@pythonScopeToString(SCOPE,X))).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=assign(V,EX), _statement_context(SCOPE,X,XS), V!=X.
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=assert(E), _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=noop, _statement_context(SCOPE,X,XS).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=seq2(STM1,STM2), _statement_latest((r,SCOPE),X,XS).
_statement_latest(SCOPE,X,XE) :- _statement_querySSA(SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_changed(STMT,X), XE=variable(loc(@pythonScopeToString(SCOPE,X))).
_statement_latest(SCOPE,X,XE) :- _statement_querySSA(SCOPE,STMT), STMT=if(EXPR,THEN,ELSE), _statement_context(SCOPE,X,XE), not _statement_changed(STMT,X).
_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=statement_python(CODE), _statement_pythonVarsResult(CODE,(X,TYPES)), XS=variable(loc(@pythonScopeToString(SCOPE,X))).


_statement_definedLatest(SCOPE,X) :- _statement_latest(SCOPE,X,XE).
variable_define(dummy,loc(@pythonScopeToString(SCOPE,X)),XI) :- _statement_querySSA(SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((t,SCOPE),X,XT), _statement_latest((e,SCOPE),X,XE),
XI=operation(ite,(COND,(XT,(XE,())))).
variable_define(dummy,loc(@pythonScopeToString(SCOPE,X)),XI) :- _statement_querySSA(SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((t,SCOPE),X,XT), not _statement_definedLatest((e,SCOPE),X),
XI=operation(ite,(COND,(XT,(val(none,none),())))).
variable_define(dummy,loc(@pythonScopeToString(SCOPE,X)),XI) :- _statement_querySSA(SCOPE,STMT), STMT=if(C,THEN,ELSE), _expression_contextualized(SCOPE,C,COND), _statement_latest((e,SCOPE),X,XE), not _statement_definedLatest((t,SCOPE),X),
XI=operation(ite,(COND,(val(none,none),(XE,())))).
variable_define(dummy,loc(@pythonScopeToString(SCOPE,X)),EX) :- _statement_querySSA(SCOPE,STMT), STMT=assign(X,E), _expression_contextualized(SCOPE,E,EX).
ensure(daummy,EX) :- _statement_querySSA(SCOPE,STMT), STMT=assert(E), _expression_contextualized(SCOPE,E,EX).

%%% TODO: add bad / error handling


variable_define(LBL,EX,val(none,none)) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), not _execution_isRunning(PRG).
variable_define(LBL,EX,V) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), _execution_succeeds(PRG,STMT), _statement_latest((PRG,()),X,V), _execution_isRunning(PRG).
variable_define(LBL,EX,val(none,none)) :- _execution_outputVar(PRG,X,EX), _execution_declare(LBL,PRG,STMT,INS,OUTS), _execution_succeeds(PRG,STMT), not _execution_ou_proj(PRG,X), _execution_isRunning(PRG).

%%% TODO: temp
_execution_succeeds(PRG,STMT) :- _execution_declare(LBL,PRG,STMT,INS,OUTS).


_statement_context((PRG,()),X,variable(execution_input(PRG,X))) :- _execution_declare(LBL,PRG,STMT,INS,OUTS), X=@pythonListElements(INS).


_statement_context((l,SCOPE),X,XS) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=seq2(S1,S2).
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=seq2(S1,S2), _statement_latest((l,SCOPE),X,X2).
_statement_context((r,SCOPE),X,X2) :- _statement_querySSA(SCOPE,STMT), STMT=seq2(S1,S2), _statement_latest((l,SCOPE),X,X2).
_statement_context((t,SCOPE),X,XS) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=if(C,T,E).
_statement_context((e,SCOPE),X,XS) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=if(C,T,E).
%TODO statement_python

% TODO: can be made faster by defining subexpression/2.?
_expression_context(SCOPE,E,X,XS) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=assign(V,E).
_expression_context(SCOPE,E,X,XS) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=assert(E).
_expression_context(SCOPE,C,X,XS) :- _statement_querySSA(SCOPE,STMT), _statement_context(SCOPE,X,XS), STMT=if(C,T,E).
_expression_context(SCOPE,D,X,XS) :- _expression_context(SCOPE,E,X,XS), E=operation(O,L), D=@pythonListElements(L).
_expression_context(SCOPE,D,X,XS) :- _expression_context(SCOPE,E,X,XS), D=@pythonTupleElements(E).
_expression_context(SCOPE,D,X,XS) :- _expression_context(SCOPE,E,X,XS), E=lambda(ARGS,D), #false: X=@pythonListElements(ARGS).

_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(SCOPE,E), E=val(T,V).
_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(SCOPE,E), E=bad.
_expression_contextualized(SCOPE,E,E) :- _expression_querySSA(SCOPE,E), E=python(CODE).
_expression_contextualized(SCOPE,E,XS) :- _expression_querySSA(SCOPE,E), E=variable(X), _expression_context(SCOPE,E,X,XS).
%TODO other vars!
_expression_contextualizedListAux(SCOPE,E,ARGS,N,()) :- _expression_querySSA(SCOPE,E), E=operation(O,ARGS), _length(ARGS,N).
_expression_contextualizedListAux(SCOPE,E,ARGS,IDX,(DC,L)) :- _expression_contextualizedListAux(SCOPE,E,ARGS,IDX+1,L),
   _expression_index(ARGS,IDX,D), _expression_contextualized(SCOPE,D,DC).
_expression_contextualized(SCOPE,E,operation(O,L)) :- _expression_contextualizedListAux(SCOPE,E,ARGS,0,L), E=operation(O,ARGS).
% TODO: operators

_expression_contextualizedListAux(SCOPE,E,ARGS,N,()) :- _expression_querySSA(SCOPE,E), _expression_isTuple(E,N,ARGS).
_expression_contextualized(SCOPE,E,@pythonReflect(function,(),N,L)) :- _expression_contextualizedListAux(SCOPE,E,ARGS,0,L), _expression_isTuple(E,N,ARGS).






%_statement_latest(SCOPE,X,XS) :- _statement_querySSA(SCOPE,STMT), STMT=statement_python(CODE), _statement_pythonVarsResult(CODE,(X,TYPES)), XS=variable(loc(@pythonScopeToString(SCOPE,X))).

*%