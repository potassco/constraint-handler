#defined execution_declare/5.
#defined execution_declare/4.
#defined execution_run/2.
#defined execution_run/1.
#defined _statement_query/2.

execution_declare(_label_anonymous,NAME,STMT,INS,OUTS) :- execution_declare(NAME,STMT,INS,OUTS).
execution_run(_label_anonymous,NAME) :- execution_run(NAME).

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_declare(CNAME,NAME,STMT,INS,OUTS).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), execution_run(CNAME,NAME).

%%%%%%%%%%%%%%%%% interface: execution_run/1 execution_assign/3 execution_output/4 execution_declare/3
_execution_declare(NAME,STMT,INS,OUTS) :- execution_declare(CNAME,NAME,STMT,INS,OUTS), engine(CNAME,compile).
_execution_input_var(NAME,X) :- _execution_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(INS).
_execution_output_var(NAME,X) :- _execution_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(OUTS).
_execution_run(NAME,STMT) :- _execution_declare(NAME,STMT,INS,OUTS), execution_run(CNAME,NAME), engine(CNAME,compile).
%_warning(("undeclared run",NAME)) :- execution_run(NAME), not execution_declare(_,NAME,_).

_execution_in(NAME,X,V) :- _execution_run(NAME,STMT), _execution_input_var(NAME,X), _se_value(variable(execution_input(NAME,X)),V).

_se_assign(_internal,variable(execution_output(NAME,X)),V) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_succeeds(NAME,STMT), _execution_ou(NAME,X,V).
_se_assign(_internal,variable(execution_output(NAME,X)),V) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_succeeds(NAME,STMT), _execution_in(NAME,X,V), not _execution_ou_proj(NAME,X).
_se_assign(_internal,variable(execution_output(NAME,X)),val(none,none)) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_succeeds(NAME,STMT), not _execution_input_var(NAME,X), not _execution_ou_proj(NAME,X).
_se_assign(_internal,variable(execution_output(NAME,X)),bad) :- _execution_output_var(NAME,X), _execution_declare(NAME,STMT,INS,OUTS), _execution_fails(NAME,STMT).

_execution_ou_proj(NAME,X) :- _execution_ou(NAME,X,V).

%%%%%%%%%%%%%%%%% _statement_query,
_statement_query((NAME,()),STMT) :- execution_declare(CNAME,NAME,STMT,INS,OUTS).
_statement_query(SCOPE,STM1) :- _statement_query(SCOPE,seq2(STM1,STM2)).
_statement_query(SCOPE,STM2) :- _statement_query(SCOPE,seq2(STM1,STM2)).
_statement_query(SCOPE,THEN) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(SCOPE,ELSE) :- _statement_query(SCOPE,if(EXPR,THEN,ELSE)).
_statement_query(SCOPE,BODY) :- _statement_query(SCOPE,while(MAX,EXPR,BODY)).

%%%%%%%%%%%%%%%%% noop
_execution_succeeds(NAME,noop) :- _execution_run(NAME,noop).

%%%%%%%%%%%%%%%%% seq2
_execution_run((subl,NAME),STMT1) :- _execution_run(NAME,seq2(STMT1,STMT2)).
_execution_run((subr,NAME),STMT2) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_succeeds((subl,NAME),STMT1).
_execution_in((subl,NAME),X,V) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_in(NAME,X,V).
_execution_in((subr,NAME),X,V) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_ou((subl,NAME),X,V), _execution_succeeds((subl,NAME),STMT1).
_execution_in((subr,NAME),X,V) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_in(NAME,X,V), not _execution_ou_proj((subl,NAME),X), _execution_succeeds((subl,NAME),STMT1).
_execution_ou(NAME,X,V) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_ou((subr,NAME),X,V), _execution_succeeds((subr,NAME),STMT2).
_execution_ou(NAME,X,V) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_ou((subl,NAME),X,V), not _execution_ou_proj((subr,NAME),X), _execution_succeeds((subr,NAME),STMT2).
_execution_succeeds(NAME,seq2(STMT1,STMT2)) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_succeeds((subr,NAME),STMT2).
_execution_fails(NAME,seq2(STMT1,STMT2)) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_fails((subl,NAME),STMT1).
_execution_fails(NAME,seq2(STMT1,STMT2)) :- _execution_run(NAME,seq2(STMT1,STMT2)), _execution_fails((subr,NAME),STMT2).

%%%%%%%%%%%%%%%%% _execution_equery -> _execution_evaled
%_execution_eval_aux(NAME,EXPR,EXP2) :- _execution_equery(NAME,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
%direct_query(EXP2) :- _execution_eval_aux(NAME,EXPR,EXP2).
_execution_eval_aux(NAME,STMT,EXPR,EXP2) :- _execution_equery(NAME,STMT,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
direct_query(EXP2) :- _execution_eval_aux(NAME,STMT,EXPR,EXP2).
_set_declare(_internal,local(NAME,X)) :- direct_query(local(NAME,X)), _execution_in(NAME,X,set(L)).
_set_assign(_internal,local(NAME,X),set(L)) :- direct_query(local(NAME,X)), _execution_in(NAME,X,set(L)), set(L)=@pythonListElements(L).
_se_value(local(NAME,X),V) :- direct_query(local(NAME,X)), _execution_in(NAME,X,V).
%_execution_evaled(NAME,EXPR,val(T,VAL)) :- _execution_eval_aux(NAME,EXPR,EXP2), _se_value(EXP2,val(T,VAL)).
_execution_evaled(NAME,STMT,EXPR,V) :- _execution_eval_aux(NAME,STMT,EXPR,EXP2), _se_value(EXP2,V).


%%%%%%%%%%%%%%%%% assign
_execution_equery(NAME,assign(X,EXPR),EXPR) :- _execution_run(NAME,assign(X,EXPR)).
_execution_succeeds(NAME,assign(X,EXPR)) :- _execution_run(NAME,assign(X,EXPR)), _execution_evaled(NAME,assign(X,EXPR),EXPR,V), V!=bad.
_execution_fails(NAME,assign(X,EXPR)) :- _execution_run(NAME,assign(X,EXPR)), _execution_evaled(NAME,assign(X,EXPR),EXPR,bad).
%_execution_ou(NAME,Y,V) :- _execution_run(NAME,assign(X,EXPR)), _execution_in(NAME,Y,V), X!=Y. % TODO:???
_execution_ou(NAME,X,V) :- _execution_run(NAME,assign(X,EXPR)), _execution_evaled(NAME,assign(X,EXPR),EXPR,V).


%%%%%%%%%%%%%%%%% assert
_execution_equery(NAME,assert(EXPR),EXPR) :- _execution_run(NAME,assert(EXPR)).
:- _execution_run(NAME,assert(EXPR)), _execution_evaled(NAME,assert(EXPR),EXPR,V), V!=val(bool,true), V!=bad.
_execution_succeeds(NAME,assert(EXPR)) :- _execution_run(NAME,assert(EXPR)), _execution_evaled(NAME,assert(EXPR),EXPR,V), V!=bad.
_execution_fails(NAME,assert(EXPR)) :- _execution_run(NAME,assert(EXPR)), _execution_evaled(NAME,assert(EXPR),EXPR,bad).


%%%%%%%%%%%%%%%%% statement_python
_direct_implode(V) :- _execution_run(NAME,statement_python(CODE)), _execution_in(NAME,X,V).
_execution_mapAux(NAME,#inf,()) :- _execution_run(NAME,statement_python(STR)).
_execution_mapAux(NAME,Y,((Y,W),M)) :- _execution_mapAux(NAME,X,M), _execution_in(NAME,Y,V), X < Y, _direct_imploded(V,W), #false : _execution_in(NAME,Z,_), X < Z, Z < Y.
_execution_mapped(NAME,M) :- _execution_mapAux(NAME,X,M), #false : _execution_in(NAME,Y,_), X < Y.

_execution_exec(NAME,R) :- _execution_run(NAME,statement_python(STR)), _execution_mapped(NAME,M), R=@pythonExec(statement_python(STR),M,ID), _main_solverIdentifier(ID).
:- _execution_exec(NAME,failIntegrity).
_execution_ou(NAME,X,V) :- _execution_run(NAME,statement_python(STR)), _execution_exec(NAME,(X,V)).
_execution_succeeds(NAME,statement_python(STR)) :- _execution_run(NAME,statement_python(STR)), _execution_exec(NAME,true).
_execution_fails(NAME,statement_python(STR)) :- _execution_run(NAME,statement_python(STR)), _execution_exec(NAME,error(KIND,MSG)).
_warning(KIND,(NAME,()),(STR,MSG,NAME)) :- _execution_run(NAME,statement_python(STR)), _execution_exec(NAME,error(KIND,MSG)).

%_statement_extract_vars(SCOPE,INS,OUS) :- _statement_query(SCOPE,statement_python(S)), _main_solverIdentifier(ID), (INS,OUS)=@pythonGetVariablesFromPython(S,ID).


%%%%%%%%%%%%%%%%% ifthenelse
_execution_equery(NAME,if(EXPR,THEN,ELSE),EXPR) :- _execution_run(NAME,if(EXPR,THEN,ELSE)).

_execution_branch((then,NAME),THEN) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_evaled(NAME,if(EXPR,THEN,ELSE),EXPR,val(bool,true)).
_execution_branch((else,NAME),ELSE) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_evaled(NAME,if(EXPR,THEN,ELSE),EXPR,val(bool,false)).
_execution_fails(NAME,if(EXPR,THEN,ELSE)) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_evaled(NAME,if(EXPR,THEN,ELSE),EXPR,V), V!=val(bool,false), V!=val(bool,true).
_execution_run(BNAME,BSTMT) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME).
_execution_in(((then;else),NAME),X,V) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_in(NAME,X,V).
_execution_ou(NAME,X,V) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_ou(BNAME,X,V), _execution_succeeds(BNAME,BSTMT).
_execution_succeeds(NAME,if(EXPR,THEN,ELSE)) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_succeeds(BNAME,BSTMT).
_execution_fails(NAME,if(EXPR,THEN,ELSE)) :- _execution_run(NAME,if(EXPR,THEN,ELSE)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_fails(BNAME,BSTMT).


%%%%%%%%%%%%%%%%% while
%_execution_equery(NAME,STMT,EXPR) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY).
%_execution_branch(NAME,skip(NAME),noop) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _execution_evaled(NAME,STMT,EXPR,val(bool,false)).
%_execution_branch(NAME,step(NAME),seq2(BODY,STMT1)) :- _execution_run(NAME,STMT), STMT = while(MAX,EXPR,BODY),
%    STMT1=while(MAX-1,EXPR,BODY), _execution_evaled(NAME,STMT,EXPR,val(bool,true)), MAX > 0.

_execution_branch((step,NAME),if(EXPR,seq2(BODY,while(MAX-1,EXPR,BODY)),noop)) :- _execution_run(NAME,while(MAX,EXPR,BODY)), MAX > 0.
_execution_run(BNAME,BSTMT) :- _execution_run(NAME,while(MAX,EXPR,BODY)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME).
_execution_in(BNAME,X,V) :- _execution_run(NAME,while(MAX,EXPR,BODY)), _execution_in(NAME,X,V), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME).
_execution_ou(NAME,X,V) :- _execution_run(NAME,while(MAX,EXPR,BODY)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_ou(BNAME,X,V), _execution_succeeds(BNAME,BSTMT).
_execution_succeeds(NAME,while(MAX,EXPR,BODY)) :- _execution_run(NAME,while(MAX,EXPR,BODY)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_succeeds(BNAME,BSTMT).
_execution_fails(NAME,while(MAX,EXPR,BODY)) :- _execution_run(NAME,while(MAX,EXPR,BODY)), _execution_branch(BNAME,BSTMT), BNAME=(_,NAME), _execution_fails(BNAME,BSTMT).
