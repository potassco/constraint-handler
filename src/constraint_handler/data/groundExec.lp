%%%%%%%%%%%%%%%%% interface: execution_run/1 execution_assign/3 execution_output/4 execution_declare/3
_gex_declare(NAME,STMT,INS,OUTS) :- execution_declare(CNAME,NAME,STMT,INS,OUTS), engine(CNAME,ground).
_gex_run(NAME,STMT,INS,OUTS) :- _gex_declare(NAME,STMT,INS,OUTS), execution_run(CNAME,NAME), engine(CNAME,ground).

_gex_inputVar(NAME,I,X,EX) :- _gex_declare(NAME,STMT,INS,OUTS), (I,X)=@pythonEnumerateElements(INS), EX=execution_input(NAME,X).
_gex_outputVar(NAME,X,EX) :- _gex_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(OUTS), EX=execution_output(NAME,X).

direct_query(V) :- _gex_run(NAME,STMT,INS,OUTS), _gex_inputVar(NAME,I,X,EX), V=variable(EX).
_direct_implode(V) :- _gex_run(NAME,STMT,INS,OUTS), _gex_inputVar(NAME,I,X,EX), V=variable(EX).
_length(inputs(NAME),N) :- _gex_run(NAME,STMT,INS,OUTS), N=@pythonListLength(INS).
_gex_mapAux(NAME,N,()) :- _gex_run(NAME,STMT,INS,OUTS), _length(inputs(NAME),N).
_gex_mapAux(NAME,I,K) :- _gex_mapAux(NAME,I+1,M), _gex_inputVar(NAME,I,X,EX), V=variable(EX), _direct_imploded(V,W), K=((X,W),M).
_gex_mapped(NAME,M) :- _gex_mapAux(NAME,0,M).


_gex_exec(NAME,R) :- _gex_run(NAME,STMT,INS,OUTS), _gex_mapped(NAME,M), R=@pythonExec(STMT,M,ID), _main_solverIdentifier(ID).
_warning(KIND,(NAME,()),("error running",MSG)) :- _gex_exec(NAME,error(KIND,MSG)).
:- _gex_exec(NAME,failIntegrity).

_ge_assign(NAME,EX,VAL) :- _gex_outputVar(NAME,X,EX), _gex_exec(NAME,true), _gex_exec(NAME,(X,VAL)).
_ge_assign(NAME,EX,val(none,none)) :- _gex_outputVar(NAME,X,EX), _gex_exec(NAME,true), not _gex_exec(NAME,(X,_)).
_se_value(EX,bad) :- _gex_outputVar(NAME,X,EX), _gex_exec(NAME,error(KIND,MSG)). %% TODO: revisit this to use _ge_assign maybe.

_direct_imploded(variable(X),V) :- ge_value(X,V), _direct_implode(variable(X)). % TODO double check
