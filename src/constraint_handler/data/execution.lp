#defined execution_declare/5.
#defined execution_run/2.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_declare(CNAME,NAME,STMT,INS,OUTS).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_run(CNAME,NAME).

%%%%%%%%%%%%%%%%% interface: execution_run/1 execution_assign/3 execution_output/4 execution_declare/3
_execution_declare(NAME,STMT,INS,OUTS) :- execution_declare(CNAME,NAME,STMT,INS,OUTS), engine(CNAME,compile).
_execution_input_var(NAME,X) :- _execution_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(INS).
_execution_output_var(NAME,X) :- _execution_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(OUTS).
_execution_run(NAME,STMT) :- _execution_declare(NAME,STMT,INS,OUTS), execution_run(CNAME,NAME), engine(CNAME,compile).
%warning(("undeclared run",NAME)) :- execution_run(NAME), not execution_declare(_,NAME,_).

_execution_in(NAME,X,val(T,V)) :- _execution_run(NAME,STMT), _execution_input_var(NAME,X), eValue(variable(execution_input(NAME,X)),T,V).

eValue(variable(execution_output(NAME,X)),T,V) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_result(NAME,STMT,success), _execution_ou(NAME,X,val(T,V)).
eValue(variable(execution_output(NAME,X)),T,V) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_result(NAME,STMT,success), _execution_in(NAME,X,val(T,V)), not _execution_ou_proj(NAME,X).


_execution_ou_proj(NAME,X) :- _execution_ou(NAME,X,V).
_execution_indexVar_proj(NAME,I) :- _execution_indexVar(NAME,I,X).

%%%%%%%%%%%%%%%%% _execution_query,
_execution_query(NAME,STMT) :- _execution_declare(NAME,STMT,INS,OUTS).


%%%%%%%%%%%%%%%%% noop
_execution_result(NAME,STMT,success) :- _execution_run(NAME,STMT), STMT = noop.

%%%%%%%%%%%%%%%%% seq2
_execution_query(subl(NAME),STMT1) :- _execution_query(NAME,STMT), STMT = seq2(STMT1,STMT2).
_execution_query(subr(NAME),STMT2) :- _execution_query(NAME,STMT), STMT = seq2(STMT1,STMT2).
_execution_run(subl(NAME),STMT1) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2).
_execution_run(subr(NAME),STMT2) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_result(subl(NAME),STMT1,success).
_execution_in(subl(NAME),X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_in(NAME,X,V).
_execution_in(subr(NAME),X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_ou(subl(NAME),X,V), _execution_result(subl(NAME),STMT1,success).
_execution_in(subr(NAME),X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_in(NAME,X,V), not _execution_ou_proj(subl(NAME),X), _execution_result(subl(NAME),STMT1,success).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_ou(subr(NAME),X,V), _execution_result(subr(NAME),STMT2,success).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_ou(subl(NAME),X,V), not _execution_ou_proj(subr(NAME),X), _execution_result(subr(NAME),STMT2,success).
_execution_result(NAME,STMT,success) :- _execution_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _execution_result(subr(NAME),STMT2,success).

%%%%%%%%%%%%%%%%% _execution_equery -> _execution_evaled
%_execution_eval_aux(NAME,EXPR,EXP2) :- _execution_equery(NAME,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
%direct_query(EXP2) :- _execution_eval_aux(NAME,EXPR,EXP2).
_execution_eval_aux(NAME,STMT,EXPR,EXP2) :- _execution_equery(NAME,STMT,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
direct_query(EXP2) :- _execution_eval_aux(NAME,STMT,EXPR,EXP2).
eValue(E,T,VAL) :- direct_query(E), E=local(NAME,X), _execution_in(NAME,X,V), V=val(T,VAL).
%_execution_evaled(NAME,EXPR,V) :- _execution_eval_aux(NAME,EXPR,EXP2), eValue(EXP2,T,VAL), V=val(T,VAL).
_execution_evaled(NAME,STMT,EXPR,V) :- _execution_eval_aux(NAME,STMT,EXPR,EXP2), eValue(EXP2,T,VAL), V=val(T,VAL).


%%%%%%%%%%%%%%%%% assign
%_execution_equery(NAME,EXPR) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR).
_execution_equery(NAME,STMT,EXPR) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR).
_execution_result(NAME,STMT,success) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR).
%_execution_ou(NAME,Y,V) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR), _execution_in(NAME,Y,V), X != Y. % TODO:???
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = assign(X,EXPR), _execution_evaled(NAME,STMT,EXPR,V).

%:- run(NAME,seq()).
%:- run(NAME,assert()).


%%%%%%%%%%%%%%%%% python
_execution_indexVar(NAME,I,X) :- _execution_query(NAME,STMT), STMT = python(STR,INS,OUTS), (I,X)=@pythonEnumerateElements(INS).
_execution_mapAux(NAME,N,()) :- _execution_run(NAME,STMT), STMT = python(STR,INS,OUTS), N=@pythonListLength(INS).
_execution_mapAux(NAME,I,((X,V),M)) :- _execution_mapAux(NAME,I+1,M), _execution_indexVar(NAME,I,X), _execution_in(NAME,X,V).
_execution_mapped(NAME,M) :- _execution_mapAux(NAME,0,M).

_execution_exec(NAME,R) :- _execution_query(NAME,STMT), STMT = python(STR,INS,OUTS), _execution_mapped(NAME,M), R=@pythonExecStmt(STR,M,OUTS).
_execution_ou(NAME,X,V) :- _execution_query(NAME,STMT), STMT = python(STR,INS,OUTS), _execution_exec(NAME,(X,V)).
_execution_result(NAME,STMT,success) :- _execution_query(NAME,STMT), STMT = python(STR,INS,OUTS), _execution_exec(NAME,true).
warning(("error running",NAME,STMT,MSG)) :- _execution_query(NAME,STMT), STMT = python(STR,INS,OUTS), _execution_exec(NAME,error(MSG)).



%%%%%%%%%%%%%%%%% ifthenelse
_execution_query(then(NAME),THEN) :- _execution_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE).
_execution_query(else(NAME),ELSE) :- _execution_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE).
_execution_equery(NAME,STMT,EXPR) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE).

_execution_branch(NAME,then(NAME),THEN) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_evaled(NAME,STMT,EXPR,val(bool,true)).
_execution_branch(NAME,else(NAME),ELSE) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_evaled(NAME,STMT,EXPR,val(bool,false)).
_execution_run(BNAME,BSTMT) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(NAME,BNAME,BSTMT).
_execution_in((then(NAME);else(NAME)),X,V) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_in(NAME,X,V).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(NAME,BNAME,BSTMT), _execution_ou(BNAME,X,V), _execution_result(BNAME,BSTMT,success).
_execution_result(NAME,STMT,success) :- _execution_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _execution_branch(NAME,BNAME,BSTMT), _execution_result(BNAME,BSTMT,success).



%%%%%%%%%%%%%%%%% while
%_execution_query(body(NAME),BODY) :- _execution_query(NAME,STMT), STMT = while(EXPR,BODY).
%_execution_equery(NAME,STMT,EXPR) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY).
%_execution_branch(NAME,skip(NAME),noop) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_evaled(NAME,STMT,EXPR,val(bool,false)).
%_execution_branch(NAME,step(NAME),seq2(BODY,STMT1)) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY),
%    STMT1=while(MAX-1,EXPR,BODY), _execution_evaled(NAME,STMT,EXPR,val(bool,true)), MAX > 0.

_execution_branch(NAME,step(NAME),if(EXPR,seq2(BODY,STMT1),noop)) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), STMT1=while(MAX-1,EXPR,BODY), MAX > 0.
_execution_run(BNAME,BSTMT) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(NAME,BNAME,BSTMT).
_execution_in(BNAME,X,V) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_in(NAME,X,V), _execution_branch(NAME,BNAME,BSTMT).
_execution_ou(NAME,X,V) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(NAME,BNAME,BSTMT), _execution_ou(BNAME,X,V), _execution_result(BNAME,BSTMT,success).
_execution_result(NAME,STMT,success) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_branch(NAME,BNAME,BSTMT), _execution_result(BNAME,BSTMT,success).
