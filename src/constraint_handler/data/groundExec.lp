%%%%%%%%%%%%%%%%% interface: execution_run/1 execution_assign/3 execution_output/4 execution_declare/3
_gex_declare(NAME,STMT,INS,OUTS) :- execution_declare(CNAME,NAME,STMT,INS,OUTS), engine(CNAME,ground).
_gex_run(NAME,STMT,INS,OUTS) :- _gex_declare(NAME,STMT,INS,OUTS), execution_run(CNAME,NAME), engine(CNAME,ground).

_gex_inputVar(NAME,I,X,EX) :- _gex_declare(NAME,STMT,INS,OUTS), (I,X)=@pythonEnumerateElements(INS), EX=execution_input(NAME,X).
_gex_outputVar(NAME,X,EX) :- _gex_declare(NAME,STMT,INS,OUTS), X=@pythonListElements(OUTS), EX=execution_output(NAME,X).

direct_query(V) :- _gex_run(NAME,STMT,INS,OUTS), _gex_inputVar(NAME,I,X,EX), V=variable(EX).
_direct_implode(V) :- _gex_run(NAME,STMT,INS,OUTS), _gex_inputVar(NAME,I,X,EX), V=variable(EX).
_gex_mapAux(NAME,N,()) :- _gex_run(NAME,STMT,INS,OUTS), N=@pythonListLength(INS).
_gex_mapAux(NAME,I,K) :- _gex_mapAux(NAME,I+1,M), _gex_inputVar(NAME,I,X,EX), V=variable(EX), _direct_imploded(V,W), K=((X,W),M).
_gex_mapped(NAME,M) :- _gex_mapAux(NAME,0,M).


_gex_exec(NAME,R) :- _gex_run(NAME,STMT,INS,OUTS), _gex_mapped(NAME,M), R=@pythonExec(STMT,M,ID), _main_solverIdentifier(ID).
warning(("error running",NAME,MSG)) :- _gex_exec(NAME,error(MSG)).
:- _gex_exec(NAME,failIntegrity).

value(EX,val(T,V)) :- _gex_outputVar(NAME,X,EX), _gex_exec(NAME,true), _gex_exec(NAME,(X,val(T,V))).
value(EX,val(none,none)) :- _gex_outputVar(NAME,X,EX), _gex_exec(NAME,true), not _gex_exec(NAME,(X,_)).

_direct_imploded(variable(X),V) :- ge_value(X,V), _direct_implode(variable(X)). % TODO double check
