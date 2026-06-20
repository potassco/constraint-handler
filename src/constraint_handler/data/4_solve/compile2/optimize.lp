% _optimize_maximizeSum(LBL,E,X,P) :- _passed(compile2,LBL,optimize_maximizeSum(E,X,P)), engine(LBL,compile2).
% _optimize_precision(PREC,PRIO) :- _passed(compile2,LBL,optimize_precision(PREC,PRIO)).

% _optimize_se_component(operation(floor,(operation(mult,(E,(PREC,()))),())),X,P) :- _optimize_maximizeSum(LBL,E,X,P),
%   _optimize_precision(PREC,P), not type_expression(E,bool).
% _optimize_se_component(operation(floor,(operation(mult,(operation(ite,(E,(val(int,1),(val(int,0),())))),(PREC,()))),())),X,P) :- _optimize_maximizeSum(LBL,E,X,P),
%   _optimize_precision(PREC,P), type_expression(E,bool).

% direct_query(E) :- _optimize_se_component(E,X,P).

% #maximize { I@P,X : _optimize_se_component(E,X,P), _se_value(E,val(int,I)) }.

%%% Abdallah: is it ensured that there is always an optimize precision for each Prio?
%%% Abdallah: why floor not round?
#maximize { @pythonScaleInteger(Value, Scale)@Prio,ID :
             _passed(compile2,_,optimize_maximizeSum(Expr,ID,Prio)),
             _passed(compile2,_,optimize_precision(ScaleExpr,Prio)), %%% Abdallah: is the LBL needed here?
             _se_value(ScaleExpr,val((float;int),Scale)),
             _se_value(Expr,val((float;int;bool),Value)) }.

_optimize_maximizeSum(LBL,E,X,P) :- _passed(compile2,LBL,optimize_maximizeSum(E,X,P)), engine(LBL,compile2). %see issue #298
