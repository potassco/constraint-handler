operator_declare(float_from_int,(int,()),float).
_computedIdx(E,val(float,F0)) :- _computeIdx(E,float_from_int), _computeIdx(E,0,val(int,I0)), F0=@pythonFloatFromInt(I0).

operator_declare(int_from_float,(float,()),int).
_computedIdx(E,val(int,I0)) :- _computeIdx(E,int_from_float), _computeIdx(E,0,val(float,F0)), I0=@pythonIntFromFloat(F0).

#script (python)

def pythonFloatFromInt(clI):
    pI = myClorm.cltopy(clI,int)
    pF = float(pI)
    return myClorm.pytocl(pF)

def pythonIntFromFloat(clF):
    pF = myClorm.cltopy(clF,float)
    pI = int(pF)
    return myClorm.pytocl(pI)
#end.
