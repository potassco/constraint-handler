%%%%%%%%%%%%%%%%% interface: execution_run/1 execution_assign/3 execution_output/4 execution_declare/3
_gex_declare(NAME,STMT,INS,OUTS) :- _execution_declare(LBL,NAME,STMT,INS,OUTS), engine(LBL,ground).
_gex_run(NAME,STMT,INS,OUTS) :- _gex_declare(NAME,STMT,INS,OUTS), _passed(sugar,execution_run(LBL,NAME)), engine(LBL,ground).

_gex_inputVar(NAME,I,X,execution_input(NAME,X)) :- _gex_declare(NAME,STMT,INS,OUTS), (I,X)=@pythonEnumerateElements(INS).

direct_query(variable(EX)) :- _gex_run(NAME,STMT,INS,OUTS), _gex_inputVar(NAME,I,X,EX).
_direct_implode(variable(EX)) :- _gex_run(NAME,STMT,INS,OUTS), _gex_inputVar(NAME,I,X,EX).
_gex_mapAux(NAME,N,()) :- _gex_run(NAME,STMT,INS,OUTS), N=@pythonListLength(INS).
_gex_mapAux(NAME,I,((X,W),M)) :- _gex_mapAux(NAME,I+1,M), _gex_inputVar(NAME,I,X,EX), _direct_imploded(variable(EX),W).
_gex_mapped(NAME,M) :- _gex_mapAux(NAME,0,M).


_gex_exec(NAME,R) :- _gex_run(NAME,STMT,INS,OUTS), _gex_mapped(NAME,M), R=@pythonExec(STMT,M,ID), _main_solverIdentifier(ID).
_warning(KIND,(NAME,()),("error running",MSG)) :- _gex_exec(NAME,error(KIND,MSG)).
:- _gex_exec(NAME,failIntegrity).

_ge_assign(NAME,EX,VAL) :- _execution_outputVar(NAME,X,EX), _gex_exec(NAME,true), _gex_exec(NAME,(X,VAL)).
_ge_assign(NAME,EX,val(none,none)) :- _execution_outputVar(NAME,X,EX), _gex_exec(NAME,true), not _gex_exec(NAME,(X,_)).
_execution_fails(NAME,STMT) :- _gex_exec(NAME,error(KIND,MSG)), _gex_declare(NAME,STMT,INS,OUTS).

_direct_imploded(variable(X),V) :- ge_value(X,V), _direct_implode(variable(X)). % TODO double check
