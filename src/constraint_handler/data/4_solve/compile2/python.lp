%%% creating the parameter list
_python_operation(named,ExprList) :-
    _expression(compile2, operation(pythonExtract(PythonStatement, PythonExpression), ExprList)).
_python_operation(positional,ExprList) :-
    _expression(compile2, operation(python(PythonExpression), ExprList)).

_python_param(ExprList, N, ()) :-
    _python_operation(_,ExprList),
    N = @pythonListLength(ExprList).

_python_param(ExprList, Idx, ((VariableName, Val), Tail)) :-
    _python_operation(named,ExprList),
    (Idx, Arg) = @pythonEnumerateElements(ExprList),
    Arg = (VariableNameExpr, Expr),
    _se_value(VariableNameExpr, VariableName),
    _se_value(Expr, Val),
    Val = (val(_,_); bad),
    _python_param(ExprList, Idx+1, Tail).
_python_param(ExprList, Idx, (Val, Tail)) :-
    _python_operation(positional,ExprList),
    (Idx, Arg) = @pythonEnumerateElements(ExprList),
    Arg = Expr,
    _se_value(Expr, Val),
    Val = (val(_,_); bad),
    _python_param(ExprList, Idx+1, Tail).

_python_set_param(ExprList, Idx, #inf, ()) :-
    _python_operation(named,ExprList),
    (Idx, Arg) = @pythonEnumerateElements(ExprList),
    Arg = (VariableNameExpr, Expr),
    _se_value(Expr, set).
_python_set_param(ExprList, Idx, #inf, ()) :-
    _python_operation(positional,ExprList),
    (Idx, Arg) = @pythonEnumerateElements(ExprList),
    Arg = Expr,
    _se_value(Expr, set).

_python_set_param(ExprList, Idx, Val, (Val, Tail)) :-
    _python_operation(named,ExprList),
    (Idx, Arg) = @pythonEnumerateElements(ExprList),
    Arg = (VariableNameExpr, Expr),
    _set_contains(Expr, Val),
    _python_set_param(ExprList, Idx, ValPrev, Tail), Val > ValPrev,
    #false : _set_contains(Expr, Val2), Val2 > ValPrev, Val2 < Val.
_python_set_param(ExprList, Idx, Val, (Val, Tail)) :-
    _python_operation(positional,ExprList),
    (Idx, Arg) = @pythonEnumerateElements(ExprList),
    Arg = Expr,
    _set_contains(Expr, Val),
    _python_set_param(ExprList, Idx, ValPrev, Tail), Val > ValPrev,
    #false : _set_contains(Expr, Val2), Val2 > ValPrev, Val2 < Val.

_python_set_param_last(ExprList, Idx, ParamList) :-
    _python_set_param(ExprList, Idx, Val, ParamList),
    #false : _set_contains(Expr, Val2), Val2 > Val.

_python_param(ExprList, Idx, (set(SetTail),Tail)) :-
    _python_param(ExprList, Idx+1, Tail),
    _python_set_param_last(ExprList, Idx, SetTail).

%#################################################
%%% alternative version
% _python_set_param(ExprList, Idx, Tail, Expr, N, ()) :- 
%     _python_param(ExprList, Idx+1, Tail),
%     (Idx,Arg) = @pythonEnumerateElement(ExprList),
%     Arg = (VariableName,Expr),
%     _se_value(Expr,set),
%     N=#count { Other : _set_contains(Expr,Other) }.

% _python_set_param(ExprList, Idx, Tail, Expr, PIdx, (Val,SetTail)) :-
%     _python_set_param(ExprList, Idx, Tail, Expr, PIdx+1, SetTail),
%     _set_contains(Expr,Val),
%     PIdx = #count { Other : _set_contains(Expr,Other), Other < Val }.

% _python_param(ExprList, Idx, (set(SetTail),Tail)) :-
%     _python_set_param(ExprList, Idx, Tail, Expr, 0, SetTail).

%#################################################

    


%%% executing the python code
%% pythonExtract
_python_output(operation(pythonExtract(PythonStatement, PythonExpression), ExprList), Result):-
    _expression(compile2, operation(pythonExtract(PythonStatement, PythonExpression), ExprList)),
    _python_param(ExprList, 0, NamedParams),  % 0 means the complete list of evaluated parameters
    _main_solverIdentifiers(Magic),
    Result = @pythonEvalExpr(operation(pythonExtract(PythonStatement, PythonExpression), NamedParams), (), Magic).
%% python
_python_output(python(PythonExpression), Result):-
    _expression(compile2, python(PythonExpression)),
    _main_solverIdentifiers(Magic),
    Result = @pythonEvalExpr(python(PythonExpression), (), Magic).
_python_output(operation(python(PythonExpression), ExprList), Result):-
    _expression(compile2, operation(python(PythonExpression), ExprList)),
    _python_param(ExprList, 0, PositionalParams),  % 0 means the complete list of evaluated parameters
    _main_solverIdentifiers(Magic),
    Result = @pythonEvalExpr(operation(python(PythonExpression), PositionalParams), (), Magic).

%%% returned values
_se_value(Expr, val(Type, Value)) :-
    _expression(compile2, Expr),
    _python_output(Expr, val(Type, Value)).

%%% return set values
_se_value(Expr, set) :-
    _expression(compile2, Expr),
    _python_output(Expr, set(L)).

_set_contains(Expr, Arg) :-
    _expression(compile2, Expr),
    _python_output(Expr, set(ExprList)),
    Arg = @pythonListElements(ExprList).

%%% bad on error
_se_value(Expr, bad) :-
    _expression(compile2, Expr),
    _python_output(Expr, error(Kind, Message)).

_se_value(Expr, bad) :-  %% maybe not necessary
    _expression(compile2, Expr),
    _python_output(Expr, bad).

%%% warnings on error
_warning(Kind, (), (python, Expr, Message)) :-
    _expression(compile2, Expr),
    _python_output(Expr, error(Kind, Message)).