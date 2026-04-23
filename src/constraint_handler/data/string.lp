%%%%%%%%%%%%%%%%% eq neq
_type_extensionalEquality(string).

%%%%%%%%%%%%%%%%% length concat
operator_declare(length,(string,()),int).
operator_declare(concat,(string,(string,())),string).
_computedIdx(E,val(int,N)) :- _computeIdx(E,length), _computeIdx(E,0,val(string,S)), N=@pythonStringLength(S).
_computedIdx(E,val(string,R)) :- _computeIdx(E,concat), _computeIdx(E,0,val(string,S1)), _computeIdx(E,1,val(string,S2)), R=@pythonStringAdd(S1,S2).
