#defined type_query/1.

%%%%%%%%%%%%%%%%% type
_type(bot;int;float;bool;string;symbol;none;set;multimap).

%%%%%%%%%%%%%%%%% type_variable
_type_variable(X,T) :- _phase_active(type_check), _passed(sugar,LBL,variable_define(X,E)), _type_expression(E,T).
_type_variable(X,T) :- _phase_active(type_check), _passed(sugar,LBL,variable_domain(X,E)), _type_expression(E,T).
_type_variable(X,set) :- _phase_active(type_check), _passed(sugar,LBL,variable_declare(X,set)).
_type_variable(X,multimap) :- _phase_active(type_check), _passed(sugar,LBL,variable_declare(X,multimap)).
type_variable(X,T) :- _type_variable(X,T).

_expression_typeQuery(operation(pythonExtract("",S),())) :- _expression_typeQuery(python(S)).

%%%%%%%%%%%%%%%%% _type_expression
_type_expression(bad,bot) :- _phase_active(type_check).
_expression_typeQuery(EXPR) :- _phase_active(type_check), _expression(sugar,EXPR).
_expression_typeQuery(EXPR) :- _phase_active(type_check), type_query(EXPR).
_expression_typeQuery(variable(X)) :- _phase_active(type_check), _variable_exists(sugar,X).
_type_expression(variable(X),T) :- _expression_typeQuery(variable(X)), _type_variable(X,T).
_type_expression(val(T,V),T) :- _expression_typeQuery(val(T,V)).
_type_expression(python(S),T) :- _expression_typeQuery(python(S)), _type_expression(operation(pythonExtract("",S),()),T).
_type_expression(operation(O,ARGS),T) :- _expression_typeQuery(operation(O,ARGS)), _type_operator(O,function(TS,T)), _type_list(operation(O,ARGS),TS).
_type_expression(operation(O,ARGS),bot) :- _expression_typeQuery(operation(O,ARGS)), _operator_declared(O), not _type_operatorAcceptInput(O,TS), _type_list(operation(O,ARGS),TS).
_type_expression(operation(O,ARGS),top) :- _expression_typeQuery(operation(O,ARGS)), _type_expression(O,top).
_type_expression((H,T),(TH,TT)) :- _expression_typeQuery((H,T)), _type_expression(H,TH), _type_expression(T,TT). %TODO general tuples


_type_listArgT(E,IDX,T) :- _expression_operationIndex(sugar,E,IDX,ARG), _type_expression(ARG,T).
_type_listAux(E,N,()) :- _expression_typeQuery(E), E=operation(O,ARGS), _expression_operationLength(sugar,E,N).
_type_listAux(E,IDX,(T,TS)) :- _type_listAux(E,IDX+1,TS), _type_listArgT(E,IDX,T).
_type_list(E,TS) :- _type_listAux(E,0,TS).

% TODO lambdas
_type_expression(lambda(ARGS,E),top) :- _expression_typeQuery(lambda(ARGS,E)).



%%%%%%%%%%%%%%%%% type_operator
_type_operator(O,function(TS,T)) :- _phase_active(type_check), operator_declare(O,TS,T).
_type_operatorAcceptInput(O,TS) :- _phase_active(type_check), _expression_typeQuery(operation(O,ARGS)), _type_operator(O,function(TS,T)),  _type_list(operation(O,ARGS),TS).

% This is for variadic operators
% - All valid elements get assigned their respective rank (from the declaration).
% - If the number of elements with a rank is equal to the number of arguments,
%   then all arguments were valid.
% - If all elements were valid, the result with the highest rank will be picked as the return type

_expression_sequenceLength(type_check,E,N) :- _expression_sequence(type_check,E), N=@pythonListLength(E).
_expression_sequenceIndex(type_check,E,IDX,X) :- _expression_sequence(type_check,E), (IDX,X)=@pythonEnumerateElements(E).



operator_variadic(OP,RT) :- operator_declare_variadic(OP,T,RT,1).
_expression_sequence(type_check,TS) :- _type_list(E,TS).
_type_variadicListAux(OP,TS,N,NT,1) :- _expression_typeQuery(E), E=operation(OP,ARGS), _type_list(E,TS), _expression_sequenceLength(type_check,TS,N), operator_variadic(OP,NT).
_type_variadicListAux(OP,TS,IDX,IT,IR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR > NR.
_type_variadicListAux(OP,TS,IDX,NT,NR) :- _type_variadicListAux(OP,TS,IDX+1,NT,NR), _expression_sequenceIndex(type_check,TS,IDX,T), operator_declare_variadic(OP,T,IT,IR), IR <= NR.
_type_operator(O,function(TS,T)) :- _type_variadicListAux(O,TS,0,T,R).


%%%%%%%%%%%%%%%%% pythonExtract
%_type_expression(operation(pythonExtract(STMT,EXPR),ARGS),bool) :- _expression_typeQuery(operation(pythonExtract(STMT,EXPR),ARGS)), EXPR  = "__succeeds".
_type_pythonExtractArgs(ARGS) :- _expression_typeQuery(operation(pythonExtract(STMT,EXPR),ARGS)).
_expression_sequence(type_check,ARGS) :- _type_pythonExtractArgs(ARGS).
_type_pythonExtractAux(ARGS,N,()) :- _type_pythonExtractArgs(ARGS), _expression_sequenceLength(type_check,ARGS,N).
_type_pythonExtractAux(ARGS,IDX,((X,T),L)) :- _type_pythonExtractAux(ARGS,IDX+1,L), _expression_sequenceIndex(type_check,ARGS,IDX,(val(string,X),EXPR)), _type_expression(EXPR,T).
_type_pythonExtract(STMT,EXPR,ARGS,L,IDS) :- _expression_typeQuery(operation(pythonExtract(STMT,EXPR),ARGS)), _type_pythonExtractAux(ARGS,0,L), _main_solverIdentifiers(IDS).
_type_pythonTypeExtractResult(operation(pythonExtract(STMT,EXPR),ARGS),T) :- _type_pythonExtract(STMT,EXPR,ARGS,TS,IDS), T=@pythonTypeExtract(STMT,EXPR,TS,IDS).
_type_expression(E,T) :- _type_pythonTypeExtractResult(E,valid(T)).
_warning(KIND,(),MSG) :- _type_pythonTypeExtractResult(E,error(KIND,MSG)).


%%%%%%%%%%%%%%%%% warnings

_type_expressionTyped(E) :- _type_expression(E,T), T!=bot.
_warning(type(noConsistentType),(),X) :- _passed(sugar,LBL,variable_interface(X)), _expression_typeQuery(variable(X)), not _type_expressionTyped(variable(X)).
%_warning(type(noType),(),X) :- _expression_typeQuery(variable(X)), not _type_expressionTyped(variable(X)).
%_warning(type(notSupported),(),X) :- _type_variable(X,top).
_warning(type(untyped),(),X) :- _passed(sugar,LBL,variable_interface(X)), _type_expression(variable(X),top).


_warning(type(notSupported),(),operation(OP,ARGS)) :- _expression_typeQuery(operation(OP,ARGS)), not _type_expressionTyped(operation(OP,ARGS)).






%%%%%%%%%%%%%%%%% _expression_normal
_type_normalizeQuery(EXPR) :- _phase_active(type_check), _expression(sugar,LBL,DECL,EXPR).
_type_normal(EXPR,bad) :- _type_normalizeQuery(EXPR), not _type_expressionTyped(EXPR).
_type_normalized(EXPR) :-  _type_normal(EXPR,NXPR).

%%%%%%%%%%%%%%%%% corrections
_type_normalizeDecl(LBL,bool_evaluate(E),bool_evaluate(NE)) :- _passed(sugar,LBL,bool_evaluate(E)),
  _type_normal(E,NE).
_type_normalizeDecl(LBL,ensure(E),ensure(NE)) :- _passed(sugar,LBL,ensure(E)),
  _type_normal(E,NE).
%_type_normalizeDecl(LBL,evaluate(OP,ARGS),evaluate(NOP,NARGS)) :- _passed(sugar,LBL,evaluate(OP,ARGS)),
%  _type_normal(operation(OP,ARGS),operation(NOP,NARGS)).
_type_normalizeDecl(LBL,variable_define(X,E),variable_define(X,NE)) :- _passed(sugar,LBL,variable_define(X,E)),
  _type_normal(E,NE).
_type_normalizeDecl(LBL,variable_domain(X,E),variable_domain(X,NE)) :- _passed(sugar,LBL,variable_domain(X,E)),
  _type_normal(E,NE).
_type_normalizeDecl(LBL,set_assign(X,E),set_assign(X,NE)) :- _passed(sugar,LBL,set_assign(X,E)),
  _type_normal(E,NE).
_type_normalizeDecl(LBL,set_baseDomain(X,E),set_baseDomain(X,NE)) :- _passed(sugar,LBL,set_baseDomain(X,E)),
  _type_normal(E,NE).
_type_normalizeDecl(LBL,multimap_assign(X,K,B),multimap_assign(X,NK,NB)) :- _passed(sugar,LBL,multimap_assign(X,K,B)),
  _type_normal(K,NK), _type_normal(B,NB).
_type_normalizeDecl(LBL,multimap_assign(X,K,B),multimap_assign(X,NK,B)) :- _passed(sugar,LBL,multimap_assign(X,K,B)),
  _type_normal(K,NK), not _type_normalized(B).
_type_normalizeDecl(LBL,multimap_assign(X,K,B),multimap_assign(X,K,NB)) :- _passed(sugar,LBL,multimap_assign(X,K,B)),
  not _type_normalized(K), _type_normal(B,NB).
_type_normalizeDecl(LBL,optimize_component(E,PREC,ID,PRIO),optimize_component(NE,NPREC,ID,PRIO)) :- _passed(sugar,LBL,optimize_component(E,PREC,ID,PRIO)),
  _type_normal(E,NE),
  _type_normal(PREC,NPREC).
_type_normalizeDecl(LBL,optimize_component(E,PREC,ID,PRIO),optimize_component(E,NPREC,ID,PRIO)) :- _passed(sugar,LBL,optimize_component(E,PREC,ID,PRIO)),
  not _type_normalized(E),
  _type_normal(PREC,NPREC).
_type_normalizeDecl(LBL,optimize_component(E,PREC,ID,PRIO),optimize_component(NE,PREC,ID,PRIO)) :- _passed(sugar,LBL,optimize_component(E,PREC,ID,PRIO)),
  _type_normal(E,NE),
  not _type_normalized(PREC).
_type_normalizeDecl(LBL,preference_holds(E,K),preference_holds(NE,K)) :- _passed(sugar,LBL,preference_holds(E,K)),
  _type_normal(E,NE).


_passed(correction(type_normalize,rem),LBL,DECL) :- _type_normalizeDecl(LBL,DECL,NECL).
_passed(correction(type_normalize,add),LBL,NECL) :- _type_normalizeDecl(LBL,DECL,NECL).

_warning(correction(type_check),(),DECL) :- _type_normalizeDecl(LBL,DECL,NECL), #false: _passed(internal_declaration,LBL2,DECL).
