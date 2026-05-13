%%%%%%%%%%%%%%%%% _expression_query from ensure evaluate
_expression_query(sugar,_global,E) :- _passed(sugar,ensure(LBL,E)).
_expression_query(sugar,_global,operation(OP,ARGS)) :- _passed(sugar,evaluate(LBL,OP,ARGS)).

%%%%%%%%%%%%%%%%% _expression_query from variables
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,variable_define(LBL,X,E)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,variable_declare(LBL,X,D)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,variable_domain(LBL,X,E)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,set_declare(LBL,X)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,set_assign(LBL,X,E)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,set_baseDomain(LBL,X,E)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,multimap_declare(LBL,X)).
_expression_query(sugar,_global,variable(X)) :- _passed(sugar,multimap_assign(LBL,X,K,B)).
_expression_query(sugar,_global,E) :- _passed(sugar,variable_define(LBL,X,E)).
_expression_query(sugar,_global,E) :- _passed(sugar,variable_domain(LBL,X,E)).
_expression_query(sugar,_global,E) :- _passed(sugar,set_assign(LBL,X,E)).
_expression_query(sugar,_global,E) :- _passed(sugar,set_baseDomain(LBL,X,E)).
_expression_query(sugar,_global,(K;B)) :- _passed(sugar,multimap_assign(LBL,X,K,B)).
%%%%%%%%%%%%%%%%% _expression_query from other declarations
_expression_query(sugar,_global,E) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)).
_expression_query(sugar,_global,E) :- _passed(sugar,optimize_precision(E,PRIO)).
_expression_query(sugar,_global,E) :- _passed(sugar,preference_expressionScore(LBL,E,K)).

%%%%%%%%%%%%%%%%% _expression_query from expressions
% TODO lambda?.
_expression_query(PHASE,PRG,D) :- _expression_query(PHASE,PRG,operation(O,L)), D=@pythonListElements(L).
_expression_query(PHASE,PRG,D) :- _expression_query(PHASE,PRG,T), D=@pythonTupleElements(T).
%_expression_query(SCOPE,D) :- _expression_query(SCOPE,pythonExtract(MAP,PSTMT,PEXPR)), (_,D)=@pythonListElements(MAP).

%%%%%%%%%%%%%%%%% _expression_query from statements
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,assert(EXPR)).
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,assign(X,EXPR)).
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).
%_expression_query(SCOPE,EXPR) :- _statement_query(SCOPE,while(MAX,EXPR,BODY)).

%%%%%%%%%%%%%%%%% _expression_query from query
_expression_query(sugar,_global,EXPR) :- _expression_query(defaultArgs,EXPR).
_expression_query(wf_check,EXPR) :- _expression_query(sugar,PRG,EXPR).
_expression_query(solve,EXPR) :- _expression_query(wf_check,EXPR).


_expression_sequenceHelper(sugar,ARGS) :- _expression_sequenceHelper(defaultArgs,ARGS).
_expression_sequenceHelper(wf_check,ARGS) :- _expression_sequenceHelper(sugar,ARGS).
_expression_sequenceHelper(type_check,ARGS) :- _expression_sequenceHelper(wf_check,ARGS).
_expression_sequenceHelper(solve,ARGS) :- _expression_sequenceHelper(type_check,ARGS).
%%%%%%%%%%%%%%%%% _expression_index _expression_isTuple
_expression_sequenceHelper(defaultArgs,ARGS) :- _expression_query(defaultArgs,operation(O,ARGS)).
_expression_sequenceHelper(defaultArgs,EXPR) :- _expression_query(defaultArgs,EXPR).

_length(defaultArgs,ARGS,N) :- _expression_sequenceHelper(defaultArgs,ARGS), N=@pythonListLength(ARGS).
_expression_index(defaultArgs,ARGS,IDX,X) :- _expression_sequenceHelper(defaultArgs,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(defaultArgs,E,N,ARGS) :- _expression_sequenceHelper(defaultArgs,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(defaultArgs,ARGS,N) :- _expression_isTuple(defaultArgs,E,N,ARGS).
_expression_index(defaultArgs,ARGS,IDX,X) :- _expression_isTuple(defaultArgs,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).

_length(sugar,ARGS,N) :- _expression_sequenceHelper(sugar,ARGS), N=@pythonListLength(ARGS).
_expression_index(sugar,ARGS,IDX,X) :- _expression_sequenceHelper(sugar,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(sugar,E,N,ARGS) :- _expression_sequenceHelper(sugar,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(sugar,ARGS,N) :- _expression_isTuple(sugar,E,N,ARGS).
_expression_index(sugar,ARGS,IDX,X) :- _expression_isTuple(sugar,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).

_length(wf_check,ARGS,N) :- _expression_sequenceHelper(wf_check,ARGS), N=@pythonListLength(ARGS).
_expression_index(wf_check,ARGS,IDX,X) :- _expression_sequenceHelper(wf_check,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(wf_check,E,N,ARGS) :- _expression_sequenceHelper(wf_check,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(wf_check,ARGS,N) :- _expression_isTuple(wf_check,E,N,ARGS).
_expression_index(wf_check,ARGS,IDX,X) :- _expression_isTuple(wf_check,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).

_length(type_check,ARGS,N) :- _expression_sequenceHelper(type_check,ARGS), N=@pythonListLength(ARGS).
_expression_index(type_check,ARGS,IDX,X) :- _expression_sequenceHelper(type_check,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(type_check,E,N,ARGS) :- _expression_sequenceHelper(type_check,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(type_check,ARGS,N) :- _expression_isTuple(type_check,E,N,ARGS).
_expression_index(type_check,ARGS,IDX,X) :- _expression_isTuple(type_check,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).

_length(solve,ARGS,N) :- _expression_sequenceHelper(solve,ARGS), N=@pythonListLength(ARGS).
_expression_index(solve,ARGS,IDX,X) :- _expression_sequenceHelper(solve,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
_expression_isTuple(solve,E,N,ARGS) :- _expression_sequenceHelper(solve,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
_length(solve,ARGS,N) :- _expression_isTuple(solve,E,N,ARGS).
_expression_index(solve,ARGS,IDX,X) :- _expression_isTuple(solve,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).

%_length(PHASE,ARGS,N) :- _expression_sequenceHelper(PHASE,ARGS), N=@pythonListLength(ARGS).
%_expression_index(PHASE,ARGS,IDX,X) :- _expression_sequenceHelper(PHASE,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
%_expression_isTuple(PHASE,E,N,ARGS) :- _expression_sequenceHelper(PHASE,E), true=@pythonIsTuple(E), (function,(),N,ARGS)=@pythonReify(E).
%_length(PHASE,ARGS,N) :- _expression_isTuple(PHASE,E,N,ARGS).
%_expression_index(PHASE,ARGS,IDX,X) :- _expression_isTuple(PHASE,E,N,ARGS), (IDX,X)=@pythonEnumerateElements(ARGS).
