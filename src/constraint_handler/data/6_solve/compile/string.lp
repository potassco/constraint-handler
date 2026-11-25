%%%%%%%%%%%%%%%%% length concat
_python_request(E,operation(length,(val(string,S),()))) :- _computeIdx(E,length), _computeIdx(E,0,val(string,S)).
_python_request(E,operation(concat,(val(string,S1),(val(string,S2),())))) :- _computeIdx(E,concat), _computeIdx(E,0,val(string,S1)), _computeIdx(E,1,val(string,S2)).
