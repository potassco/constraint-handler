engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), exec_declare(CNAME,NAME,STMT,INS,OUTS).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), exec_run(CNAME,NAME).

%%%%%%%%%%%%%%%%% interface: exec_run/1 exec_assign/3 exec_output/4 exec_declare/3
_exec_declare(NAME,STMT,INS,OUTS) :- exec_declare(CNAME,NAME,STMT,INS,OUTS), engine(CNAME,compile).
_exec_input_var(NAME,X) :- _exec_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(INS).
_exec_output_var(NAME,X) :- _exec_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(OUTS).
_exec_run(NAME,STMT) :- _exec_declare(NAME,STMT,INS,OUTS), exec_run(CNAME,NAME), engine(CNAME,compile).
%warning(("undeclared run",NAME)) :- exec_run(NAME), not exec_declare(_,NAME,_).

_exec_in(NAME,X,val(T,V)) :- _exec_run(NAME,STMT), _exec_input_var(NAME,X), eValue(variable(exec_input(NAME,X)),T,V).

%direct_query(E) :- _exec_run(NAME,STMT), exec_assign(NAME,X,E).
%exec_input(NAME,X,val(T,V)) :- _exec_run(NAME,STMT), _exec_input_var(NAME,X), exec_assign(NAME,X,E), eValue(E,T,V).
%_exec_in(NAME,X,val(T,V)) :- _exec_run(NAME,STMT), _exec_input_var(NAME,X), exec_assign(NAME,X,E), eValue(E,T,V).
%exec_output(NAME,X,val(T,V)) :- _exec_output_var(NAME,X), _exec_declare(NAME,STMT,INS,OUTS), _exec_result(NAME,STMT,success), _exec_ou(NAME,X,val(T,V)).
%exec_output(NAME,X,val(T,V)) :- _exec_output_var(NAME,X), _exec_declare(NAME,STMT,INS,OUTS), _exec_result(NAME,STMT,success), _exec_in(NAME,X,val(T,V)), not _exec_ou_proj(NAME,X).
eValue(variable(exec_output(NAME,X)),T,V) :- _exec_output_var(NAME,X), _exec_declare(NAME,STMT,INS,OUTS), _exec_result(NAME,STMT,success), _exec_ou(NAME,X,val(T,V)).
eValue(variable(exec_output(NAME,X)),T,V) :- _exec_output_var(NAME,X), _exec_declare(NAME,STMT,INS,OUTS), _exec_result(NAME,STMT,success), _exec_in(NAME,X,val(T,V)), not _exec_ou_proj(NAME,X).


_exec_ou_proj(NAME,X) :- _exec_ou(NAME,X,V).
_exec_indexVar_proj(NAME,I) :- _exec_indexVar(NAME,I,X).

%%%%%%%%%%%%%%%%% _exec_query, 
_exec_query(NAME,STMT) :- _exec_declare(NAME,STMT,INS,OUTS).


%%%%%%%%%%%%%%%%% noop
_exec_result(NAME,STMT,success) :- _exec_run(NAME,STMT), STMT = noop.

%%%%%%%%%%%%%%%%% seq2
_exec_query(subl(NAME),STMT1) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2).
_exec_query(subr(NAME),STMT2) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2).
_exec_run(subl(NAME),STMT1) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2).
_exec_run(subr(NAME),STMT2) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_result(subl(NAME),STMT1,success).
_exec_in(subl(NAME),X,V) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_in(NAME,X,V).
_exec_in(subr(NAME),X,V) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_ou(subl(NAME),X,V), _exec_result(subl(NAME),STMT1,success).
_exec_in(subr(NAME),X,V) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_in(NAME,X,V), not _exec_ou_proj(subl(NAME),X), _exec_result(subl(NAME),STMT1,success).
_exec_ou(NAME,X,V) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_ou(subr(NAME),X,V), _exec_result(subr(NAME),STMT2,success).
_exec_ou(NAME,X,V) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_ou(subl(NAME),X,V), not _exec_ou_proj(subr(NAME),X), _exec_result(subr(NAME),STMT2,success).
_exec_result(NAME,STMT,success) :- _exec_run(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_result(subr(NAME),STMT2,success).

%%%%%%%%%%%%%%%%% _exec_equery -> _exec_evaled
%_exec_eval_aux(NAME,EXPR,EXP2) :- _exec_equery(NAME,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
%direct_query(EXP2) :- _exec_eval_aux(NAME,EXPR,EXP2).
_exec_eval_aux(NAME,STMT,EXPR,EXP2) :- _exec_equery(NAME,STMT,EXPR), EXP2=@pythonTagVars(EXPR,NAME).
direct_query(EXP2) :- _exec_eval_aux(NAME,STMT,EXPR,EXP2).
eValue(E,T,VAL) :- direct_query(E), E=local(NAME,X), _exec_in(NAME,X,V), V=val(T,VAL).
%_exec_evaled(NAME,EXPR,V) :- _exec_eval_aux(NAME,EXPR,EXP2), eValue(EXP2,T,VAL), V=val(T,VAL).
_exec_evaled(NAME,STMT,EXPR,V) :- _exec_eval_aux(NAME,STMT,EXPR,EXP2), eValue(EXP2,T,VAL), V=val(T,VAL).


%%%%%%%%%%%%%%%%% assign
%_exec_equery(NAME,EXPR) :- _exec_run(NAME,STMT), STMT = assign(X,EXPR).
_exec_equery(NAME,STMT,EXPR) :- _exec_run(NAME,STMT), STMT = assign(X,EXPR).
_exec_result(NAME,STMT,success) :- _exec_run(NAME,STMT), STMT = assign(X,EXPR).
%_exec_ou(NAME,Y,V) :- _exec_run(NAME,STMT), STMT = assign(X,EXPR), _exec_in(NAME,Y,V), X != Y. % TODO:???
_exec_ou(NAME,X,V) :- _exec_run(NAME,STMT), STMT = assign(X,EXPR), _exec_evaled(NAME,STMT,EXPR,V).

%:- run(NAME,seq()).
%:- run(NAME,assert()).


%%%%%%%%%%%%%%%%% python
_exec_indexVar(NAME,I,X) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), (I,X)=@pythonEnumerateElements(INS).

_exec_mapAux(NAME,0,()) :- _exec_run(NAME,STMT), STMT = python(STR,INS,OUTS).
_exec_mapAux(NAME,I+1,((X,V),M)) :- _exec_mapAux(NAME,I,M), _exec_indexVar(NAME,I,X), _exec_in(NAME,X,V).
_exec_mapped(NAME,M) :- _exec_mapAux(NAME,I,M), not _exec_indexVar_proj(NAME,I).

_exec_exec(NAME,R) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), _exec_mapped(NAME,M), R=@pythonExecStmt(STR,M,OUTS).
_exec_ou(NAME,X,V) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), _exec_exec(NAME,(X,V)).
_exec_result(NAME,STMT,success) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), _exec_exec(NAME,true).
warning(("error running",NAME,STMT,MSG)) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), _exec_exec(NAME,error(MSG)).



%%%%%%%%%%%%%%%%% ifthenelse
_exec_query(then(NAME),THEN) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE).
_exec_query(else(NAME),ELSE) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE).
_exec_equery(NAME,STMT,EXPR) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE).

_exec_branch(NAME,then(NAME),THEN) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_evaled(NAME,STMT,EXPR,val(bool,true)).
_exec_branch(NAME,else(NAME),ELSE) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_evaled(NAME,STMT,EXPR,val(bool,false)).
_exec_run(BNAME,BSTMT) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_branch(NAME,BNAME,BSTMT).
_exec_in((then(NAME);else(NAME)),X,V) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_in(NAME,X,V).
_exec_ou(NAME,X,V) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_branch(NAME,BNAME,BSTMT), _exec_ou(BNAME,X,V), _exec_result(BNAME,BSTMT,success).
_exec_result(NAME,STMT,success) :- _exec_run(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_branch(NAME,BNAME,BSTMT), _exec_result(BNAME,BSTMT,success).



%%%%%%%%%%%%%%%%% while
%_exec_query(body(NAME),BODY) :- _exec_query(NAME,STMT), STMT = while(EXPR,BODY).
%_exec_equery(NAME,STMT,EXPR) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY).
%_exec_branch(NAME,skip(NAME),noop) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _exec_evaled(NAME,STMT,EXPR,val(bool,false)).
%_exec_branch(NAME,step(NAME),seq2(BODY,STMT1)) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY),
%    STMT1=while(MAX-1,EXPR,BODY), _exec_evaled(NAME,STMT,EXPR,val(bool,true)), MAX > 0.

_exec_branch(NAME,step(NAME),if(EXPR,seq2(BODY,STMT1),noop)) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), STMT1=while(MAX-1,EXPR,BODY), MAX > 0.
_exec_run(BNAME,BSTMT) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _exec_branch(NAME,BNAME,BSTMT).
_exec_in(BNAME,X,V) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _exec_in(NAME,X,V), _exec_branch(NAME,BNAME,BSTMT).
_exec_ou(NAME,X,V) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _exec_branch(NAME,BNAME,BSTMT), _exec_ou(BNAME,X,V), _exec_result(BNAME,BSTMT,success).
_exec_result(NAME,STMT,success) :- _exec_run(NAME,STMT), STMT = while(MAX,EXPR,BODY), _exec_branch(NAME,BNAME,BSTMT), _exec_result(BNAME,BSTMT,success).

%*
%%%%%%%%%%%%%%%%% needs, offers, environment
%% no needs and offer from noop
_exec_needs(STMT,X) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_needs(STMT1,X).
_exec_needs(STMT,X) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_needs(STMT2,X), not _exec_offer(STMT1,X).
_exec_offer(STMT,X) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_offer((STMT1;STMT2),X).
_exec_needs(STMT,X) :- _exec_query(NAME,STMT), STMT = assign(X,EXPR), X=@pythonCollectVars(EXPR). %%% TODO: check if it's the right function
_exec_offer(STMT,X) :- _exec_query(NAME,STMT), STMT = assign(X,EXPR).

_exec_needs(STMT,X) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), X=@pythonListElements(INS).
_exec_offer(STMT,X) :- _exec_query(NAME,STMT), STMT = python(STR,INS,OUTS), X=@pythonListElements(OUTS).

%_exec_needs(STMT,X) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE), X=@pythonCollectVars(EXPR).
_exec_needs(STMT,X) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_needs((THEN;ELSE),X).
_exec_offer(STMT,X) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_offer(THEN,X), _exec_offer(ELSE,X).

_exec_environment(NAME,STMT,X) :- _exec_run(NAME,STMT), exec_assign(NAME,X,E).
_exec_environment(sub(NAME,1),STMT1,X) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_environment(NAME,STMT,X).
_exec_environment(sub(NAME,2),STMT2,X) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_environment(NAME,STMT,X).
_exec_environment(sub(NAME,2),STMT2,X) :- _exec_query(NAME,STMT), STMT = seq2(STMT1,STMT2), _exec_offer(STMT1,X).

_exec_environment(then(NAME),THEN,X) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_environment(NAME,STMT,X).
_exec_environment(else(NAME),ELSE,X) :- _exec_query(NAME,STMT), STMT = if(EXPR,THEN,ELSE), _exec_environment(NAME,STMT,X).

warning((missingVar,NAME,STMT,X)) :- _exec_query(NAME,STMT), _exec_needs(STMT,X), not _exec_environment(NAME,STMT,X).
*%


%ge_set_declare(X) :- set_declare(CNAME,X), engine(CNAME,ground).
%ge_set_assign(X,E) :- set_assign(CNAME,X,E), engine(CNAME,ground).
%
%ge_indexSetAssign(X,#inf,-1) :- ge_set_declare(X).
%ge_indexSetAssign(X,F,I+1) :- ge_indexSetAssign(X,E,I), ge_set_assign(X,F), E < F,
%   0 = #count { G : ge_set_assign(X,G), E < G, G < F }.
%ge_nbSetAssigns(X,N) :- ge_set_declare(X),
%  N = #count { E : ge_set_assign(X,E) }.

%ge_indexSetValue(X,0,()) :- ge_set_declare(X).
%ge_indexSetValue(X,I+1,(V,L)) :- ge_indexSetValue(X,I,L), ge_indexSetAssign(X,E,I), ge_result(E,T,V), T != none.
%ge_indexSetValue(X,I+1,L) :- ge_indexSetValue(X,I,L), ge_indexSetAssign(X,E,I), ge_result(E,none,V).
%ge_value(X,set,set(L)) :- ge_indexSetValue(X,I,L), ge_nbSetAssigns(X,I).

%_exec_run(sub(NAME,1),STMT) :- _exec_run(NAME,STMT), STMT = python(STR).
%_exec_in(sub(NAME,1),X,V) :- _exec_run(NAME,STMT), STMT = python(STR), _exec_in(NAME,X,V).
%_exec_has_input(NAME,X) :- _exec_in(NAME,X,V), STMT=python(STR).




#script(python)

import typing
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator


class Local(typing.NamedTuple):
    name: typing.Any
    var: evaluator.Variable


def pythonDebug(clExpr):
    #print("debug: ",clExpr)
    return clExpr

def pythonStop(clExpr):
    #print("stop: ",clExpr)
    pExpr = myClorm.cltopy(clExpr)
    if pExpr < -5:
        assert False
    return clExpr

def pythonTagVars(clExpr,clName):
    # print("pythonEvalExpr",clName,clExpr,clArgs)
    pName = myClorm.cltopy(clName)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    vars = evaluator.collectVars(pExpr)
    map = { var : Local(pName,var) for var in vars }
    pExp2 = evaluator.beta_reduction(map,pExpr)
    return myClorm.pytocl(pExp2)

#end.