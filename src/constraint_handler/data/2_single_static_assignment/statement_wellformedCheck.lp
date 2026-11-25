%%%%%%%%%%%%%%%%% _statement_query,
_statement_query(PRG,(PRG,()),STMT) :- _phase_active(statement_wellformedCheck), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS,COND)).
_statement_query(PRG,SCOPE,STM1) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,STM2) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,THEN) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(PRG,SCOPE,ELSE) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).

_statement_expressionQuery(EXPR) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_statement_expressionQuery(EXPR) :- _statement_query(PRG,SCOPE,assign(X,EXPR)).
_statement_expressionQuery(EXPR) :- _statement_query(PRG,SCOPE,assert(EXPR)).
_statement_expressionQuery(COND) :- _phase_active(statement_wellformedCheck), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS,COND)).
_statement_expressionWellformed(EXPR) :- _statement_expressionQuery(EXPR), true=@pythonIsExpr(EXPR).

%%%%%%%%%%%%%%%%% _statement_wellformed
_statement_wellformed(seq2(STM1,STM2)) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)), _statement_wellformed(STM1), _statement_wellformed(STM2).
_statement_wellformed(noop) :- _statement_query(PRG,SCOPE,noop).
_statement_wellformed(statement_python(STR)) :- _statement_query(PRG,SCOPE,statement_python(STR)), (string,_,_,_)=@pythonReify(STR).
_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)), _statement_expressionWellformed(EXPR), _statement_wellformed(THEN), _statement_wellformed(ELSE).
_statement_wellformed(assign(X,EXPR)) :- _statement_query(PRG,SCOPE,assign(X,EXPR)), _statement_expressionWellformed(EXPR).
_statement_wellformed(assert(EXPR)) :- _statement_query(PRG,SCOPE,assert(EXPR)), _statement_expressionWellformed(EXPR).



ch_core(warning_raise(statement(syntaxError),STMT,val(bool,true)),LBL) :- _statement_query(PRG,SCOPE,STMT), not _statement_wellformed(STMT), _passed(defaultArgs,LBL,execution_declare(PRG,STMT2,INS,OUTS,COND)).


%%%%%% statement atoms
ch_core(warning_raise(atom(syntaxError),execution_declare(PRG),val(bool,true)),PRG) :- _phase_active(statement_wellformedCheck), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS,COND)),
    #false: _statement_wellformed(STMT), _expression_sequenceLength(defaultArgs,INS,NI), _expression_sequenceLength(defaultArgs,OUTS,NO), _statement_expressionWellformed(COND).
%%% TODO add bad for all exec outs
