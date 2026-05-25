%%%%%%%%%%%%%%%%% _expression_query from ensure evaluate
_expression_query(sugar,E) :- _passed(sugar,ensure(LBL,E)).
_expression_query(sugar,operation(OP,ARGS)) :- _passed(sugar,evaluate(LBL,OP,ARGS)).

%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query(sugar,E) :- _passed(sugar,variable_define(LBL,X,E)).
_expression_query(sugar,E) :- _passed(sugar,variable_domain(LBL,X,E)).
_expression_query(sugar,E) :- _passed(sugar,set_assign(LBL,X,E)).
_expression_query(sugar,E) :- _passed(sugar,set_baseDomain(LBL,X,E)).
_expression_query(sugar,(K;B)) :- _passed(sugar,multimap_assign(LBL,X,K,B)).
%%%%%%%%%%%%%%%%% _expression_query from other declarations
_expression_query(sugar,E) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)).
_expression_query(sugar,E) :- _passed(sugar,optimize_precision(E,PRIO)).
_expression_query(sugar,E) :- _passed(sugar,preference_holds(LBL,E,K)).

%%%%%%%%%%%%%%%%% _expression_query from expressions
% TODO lambda?.
_expression_query(sugar,D) :- _expression_query(sugar,operation(O,L)), D=@pythonListElements(L).
_expression_query(sugar,D) :- _expression_query(sugar,T), D=@pythonTupleElements(T).

%%%%%%%%%%%%%%%%% _expression_query from statements
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,assert(EXPR)).
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,assign(X,EXPR)).
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).

%%%%%%%%%%%%%%%%% _expression_query from query
_expression_sequenceHelper(solve,ARGS) :- _expression_sequenceHelper(type_check,ARGS).

%%%%%%%%%%%%%%%%% _expression_index _expression_isTuple
_length(defaultArgs,ARGS,N) :- _expression_sequenceHelper(defaultArgs,ARGS), N=@pythonListLength(ARGS).
_expression_index(defaultArgs,ARGS,IDX,X) :- _expression_sequenceHelper(defaultArgs,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(defaultArgs,E,N,ARGS) :- _expression_sequenceHelper(defaultArgs,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(defaultArgs,ARGS,N) :- _expression_isTuple(defaultArgs,E,N,ARGS).
_expression_index(defaultArgs,ARGS,IDX,X) :- _expression_isTuple(defaultArgs,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).


_length(wf_check,ARGS,N) :- _expression_sequenceHelper(wf_check,ARGS), N=@pythonListLength(ARGS).
_expression_index(wf_check,ARGS,IDX,X) :- _expression_sequenceHelper(wf_check,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(wf_check,E,N,ARGS) :- _expression_sequenceHelper(wf_check,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(wf_check,ARGS,N) :- _expression_isTuple(wf_check,E,N,ARGS).
_expression_index(wf_check,ARGS,IDX,X) :- _expression_isTuple(wf_check,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).


_length(solve,ARGS,N) :- _expression_sequenceHelper(solve,ARGS), N=@pythonListLength(ARGS).
_expression_index(solve,ARGS,IDX,X) :- _expression_sequenceHelper(solve,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
