%%%%%%%%%%%%%%%%% _statement_query,
_statement_query(PRG,(PRG,()),STMT) :- _phase_active(statement_wellformedCheck), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)).
_statement_query(PRG,SCOPE,STM1) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,STM2) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)).
_statement_query(PRG,SCOPE,THEN) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(PRG,SCOPE,ELSE) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)).

%%%%%%%%%%%%%%%%% _statement_wellformed
_statement_wellformed(seq2(STM1,STM2)) :- _statement_query(PRG,SCOPE,seq2(STM1,STM2)), _statement_wellformed(STM1), _statement_wellformed(STM2).
_statement_wellformed(noop) :- _statement_query(PRG,SCOPE,noop).
_statement_wellformed(statement_python(STR)) :- _statement_query(PRG,SCOPE,statement_python(STR)), (string,_,_,_)=@pythonReify(STR).
_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(PRG,SCOPE,if(EXPR,THEN,ELSE)), true=@pythonIsExpr(EXPR), _statement_wellformed(THEN), _statement_wellformed(ELSE).
_statement_wellformed(assign(X,EXPR)) :- _statement_query(PRG,SCOPE,assign(X,EXPR)), true=@pythonIsExpr(EXPR).
_statement_wellformed(assert(EXPR)) :- _statement_query(PRG,SCOPE,assert(EXPR)), true=@pythonIsExpr(EXPR).



_warning(statement(syntaxError),LBL,STMT) :- _statement_query(PRG,SCOPE,STMT), not _statement_wellformed(STMT), _passed(defaultArgs,LBL,execution_declare(PRG,STMT2,INS,OUTS)).


%%%%%% statement atoms
_warning(atom(syntaxError),PRG,execution_declare(PRG)) :- _phase_active(statement_wellformedCheck), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)),
    #false: _statement_wellformed(STMT), true=@pythonIsList(INS), true=@pythonIsList(OUTS).
%%% TODO add bad for all exec outs
