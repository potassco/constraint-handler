%%%%%%%%%%%%%%%%% _statement_wellformed
_statement_wellformed(seq2(STM1,STM2)) :- _statement_query(SCOPE,seq2(STM1,STM2)), _statement_wellformed(SCOPE,STM1), _statement_wellformed(STM2).
_statement_wellformed(noop) :- _statement_query(SCOPE,noop).
_statement_wellformed(if(EXPR,THEN,ELSE)) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)), _expression_wellformed(EXPR), _statement_wellformed(SCOPE,THEN), _statement_wellformed(ELSE).
_statement_wellformed(assign(X,EXPR)) :- _statement_query(SCOPE,assign(X,EXPR)), _expression_wellformed(EXPR).
_statement_wellformed(assert(EXPR)) :- _statement_query(SCOPE,assert(EXPR)), _expression_wellformed(EXPR).
_statement_wellformed(statementPython(STR)) :- _statement_query(SCOPE,statementPython(STR)), (string,_,_,_)=@pythonReify(STR).
_statement_wellformed(while(MAX,EXPR,BODY)) :- _statement_query(SCOPE,while(MAX,EXPR,BODY)), _expression_wellformed(EXPR), _statement_wellformed(BODY).

_warning(statement(syntaxError),SCOPE,STMT) :- _statement_query(SCOPE,STMT), not _statement_wellformed(STMT).
