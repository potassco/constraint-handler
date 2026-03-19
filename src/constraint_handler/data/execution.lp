#defined execution_declare/5.
#defined execution_run/2.
#defined _statement_query/2.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_declare(CNAME,NAME,STMT,INS,OUTS).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_run(CNAME,NAME).

%%%%%%%%%%%%%%%%% interface: execution_run/1 execution_assign/3 execution_output/4 execution_declare/3
_execution_declare(NAME,STMT,INS,OUTS) :- execution_declare(CNAME,NAME,STMT,INS,OUTS), engine(CNAME,compile).
_execution_input_var(NAME,X) :- _execution_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(INS).
_execution_output_var(NAME,X) :- _execution_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(OUTS).
_execution_run(NAME,STMT) :- _execution_declare(NAME,STMT,INS,OUTS), execution_run(CNAME,NAME), engine(CNAME,compile).
%_warning(("undeclared run",NAME)) :- execution_run(NAME), not execution_declare(_,NAME,_).

_execution_in(NAME,X,V) :- _execution_run(NAME,STMT), _execution_input_var(NAME,X), E=variable(execution_input(NAME,X)), E_ID=@pythonId(E), _se_value_id(E_ID,V).

_se_assign(_internal,variable(execution_output(NAME,X)),V) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_succeeds(NAME,STMT), _execution_ou(NAME,X,V).
_se_assign(_internal,variable(execution_output(NAME,X)),V) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_succeeds(NAME,STMT), _execution_in(NAME,X,V), not _execution_ou_proj(NAME,X).
_se_assign(_internal,variable(execution_output(NAME,X)),val(none,none)) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_succeeds(NAME,STMT), not _execution_input_var(NAME,X), not _execution_ou_proj(NAME,X).
_se_assign(_internal,variable(execution_output(NAME,X)),bad) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_fails(NAME,STMT).

_execution_ou_proj(NAME,X) :- _execution_ou(NAME,X,V).

%%%%%%%%%%%%%%%%% _statement_query,
_statement_query((NAME,()),STMT) :- execution_declare(CNAME,NAME,STMT,INS,OUTS).
_statement_query(SCOPE,STM1) :- _statement_query(SCOPE,STMT), STMT = seq2(STM1,STM2).
_statement_query(SCOPE,STM2) :- _statement_query(SCOPE,STMT), STMT = seq2(STM1,STM2).
_statement_query(SCOPE,THEN) :- _statement_query(SCOPE,STMT), STMT = if(EXPR,THEN,ELSE).
_statement_query(SCOPE,ELSE) :- _statement_query(SCOPE,STMT), STMT = if(EXPR,THEN,ELSE).
_statement_query(SCOPE,BODY) :- _statement_query(SCOPE,STMT), STMT = while(MAX,EXPR,BODY).

%%%%%%%%%%%%%%%%% noop
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = noop.

%%%%%%%%%%%%%%%%% seq2
_execution_run((subl,NAME),STMT1) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2).
_execution_run((subr,NAME),STMT2) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_succeeds((subl,NAME),STMT1).
_execution_in((subl,NAME),X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_in(NAME,X,V).
_execution_in((subr,NAME),X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_ou((subl,NAME),X,V), _execution_succeeds((subl,NAME),STMT1).
_execution_in((subr,NAME),X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_in(NAME,X,V), not _execution_ou_proj((subl,NAME),X), _execution_succeeds((subl,NAME),STMT1).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_ou((subr,NAME),X,V), _execution_succeeds((subr,NAME),STMT2).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_ou((subl,NAME),X,V), not _execution_ou_proj((subr,NAME),X), _execution_succeeds((subr,NAME),STMT2).
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_succeeds((subr,NAME),STMT2).
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_fails((subl,NAME),STMT1).
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_fails((subr,NAME),STMT2).

%%%%%%%%%%%%%%%%% _execution_equery -> _execution_evaled
%_execution_eval_aux(NAME,EXPR,EXP2) :- _execution_equery(NAME,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
%direct_query(EXP2) :- _execution_eval_aux(NAME,EXPR,EXP2).
_statement_id(STMT_ID,STMT) :- _execution_run(NAME,STMT), STMT_ID=@pythonId(STMT).
_expr_id(EXPR_ID,EXPR) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR), EXPR_ID=@pythonId(EXPR).
_expr_id(EXPR_ID,EXPR) :- _execution_run(NAME,STMT), STMT = assert(EXPR), EXPR_ID=@pythonId(EXPR).
_expr_id(EXPR_ID,EXPR) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), EXPR_ID=@pythonId(EXPR).
_execution_eval_aux(NAME,STMT_ID,EXPR_ID,EXP2) :- _execution_equery(NAME,STMT_ID,EXPR_ID), _expr_id(EXPR_ID,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
direct_query(EXP2) :- _execution_eval_aux(NAME,STMT_ID,EXPR_ID,EXP2).
_set_declare(_internal,E) :- direct_query(E), E=local(NAME,X), _execution_in(NAME,X,V), V=set(L).
_set_assign(_internal,E,V) :- direct_query(E), E=local(NAME,X), _execution_in(NAME,X,V), V=set(L), V=@pythonListElements(L).
_se_value_id(E_ID,V) :- _expr_id(E_ID,E), E=local(NAME,X), _execution_in(NAME,X,V).
_execution_evaled(NAME,STMT_ID,EXPR_ID,V) :- _execution_eval_aux(NAME,STMT_ID,EXPR_ID,EXP2), EXP2_ID=@pythonId(EXP2), _se_value_id(EXP2_ID,V).


%%%%%%%%%%%%%%%%% assign
_execution_equery(NAME,STMT_ID,EXPR_ID) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR), _statement_id(STMT_ID,STMT), _expr_id(EXPR_ID,EXPR).
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = assign(X,_), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,V), V!=bad.
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = assign(X,_), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,bad).
%_execution_ou(NAME,Y,V) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR), _execution_in(NAME,Y,V), X != Y. % TODO:???
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = assign(X,_), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,V).


%%%%%%%%%%%%%%%%% assert
_execution_equery(NAME,STMT_ID,EXPR_ID) :- _execution_run(NAME,STMT), STMT = assert(EXPR), _statement_id(STMT_ID,STMT), _expr_id(EXPR_ID,EXPR).
:- _execution_run(NAME,STMT), STMT = assert(_), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,V), V != val(bool,true), V != bad.
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = assert(_), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,V), V!=bad.
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = assert(_), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,bad).


%%%%%%%%%%%%%%%%% statement_python
_direct_implode(V) :- _execution_run(NAME,STMT), STMT = statement_python(CODE), _execution_in(NAME,X,V).
_execution_mapAux(NAME,#inf,()) :- _execution_run(NAME,STMT), STMT = statement_python(STR).
_execution_mapAux(NAME,Y,K) :- _execution_mapAux(NAME,X,M), _execution_in(NAME,Y,V), X < Y, _direct_imploded(V,W), K=((Y,W),M), #false : _execution_in(NAME,Z,_), X < Z, Z < Y.
_execution_mapped(NAME,M) :- _execution_mapAux(NAME,X,M), #false : _execution_in(NAME,Y,_), X < Y.

_execution_exec(NAME,R) :- _execution_run(NAME,STMT), STMT = statement_python(STR), _execution_mapped(NAME,M), R=@pythonExec(STMT,M,ID), _main_solverIdentifier(ID).
:- _execution_exec(NAME,failIntegrity).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = statement_python(STR), _execution_exec(NAME,(X,V)).
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = statement_python(STR), _execution_exec(NAME,true).
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = statement_python(STR), _execution_exec(NAME,error(KIND,MSG)).
_warning(KIND,(NAME,()),(STR,MSG,NAME)) :- _execution_run(NAME,STMT), STMT = statement_python(STR), _execution_exec(NAME,error(KIND,MSG)).

%_statement_extract_vars(SCOPE,INS,OUS) :- _statement_query(SCOPE,STMT), STMT = statement_python(S), _main_solverIdentifier(ID), (INS,OUS)=@pythonGetVariablesFromPython(S,ID).


%%%%%%%%%%%%%%%%% ifthenelse
_execution_equery(NAME,STMT_ID,EXPR_ID) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _statement_id(STMT_ID,STMT), _expr_id(EXPR_ID,EXPR).

_execution_branch((then,NAME),THEN) :- _execution_run(NAME,STMT), STMT = if(_,THEN,ELSE), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,val(bool,true)).
_execution_branch((else,NAME),ELSE) :- _execution_run(NAME,STMT), STMT = if(_,THEN,ELSE), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,val(bool,false)).
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = if(_,THEN,ELSE), _statement_id(STMT_ID,STMT), _execution_equery(NAME,STMT_ID,EXPR_ID), _execution_evaled(NAME,STMT_ID,EXPR_ID,V), V!=val(bool,false), V!=val(bool,true).
_execution_run(BNAME,BSTMT) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME).
_execution_in(((then;else),NAME),X,V) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_in(NAME,X,V).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_ou(BNAME,X,V), _execution_succeeds(BNAME,BSTMT).
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_succeeds(BNAME,BSTMT).
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_fails(BNAME,BSTMT).


%%%%%%%%%%%%%%%%% while
%_execution_equery(NAME,STMT,EXPR) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY).
%_execution_branch(NAME,skip(NAME),noop) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_evaled(NAME,STMT,EXPR,val(bool,false)).
%_execution_branch(NAME,step(NAME),seq2(BODY,STMT1)) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY),
%    STMT1=while(MAX-1,EXPR,BODY), _execution_evaled(NAME,STMT,EXPR,val(bool,true)), MAX > 0.

_execution_branch((step,NAME),if(EXPR,seq2(BODY,STMT1),noop)) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), STMT1=while(MAX-1,EXPR,BODY), MAX > 0.
_execution_run(BNAME,BSTMT) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME).
_execution_in(BNAME,X,V) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_in(NAME,X,V), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_ou(BNAME,X,V), _execution_succeeds(BNAME,BSTMT).
_execution_succeeds(NAME,STMT) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_succeeds(BNAME,BSTMT).
_execution_fails(NAME,STMT) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_fails(BNAME,BSTMT).
