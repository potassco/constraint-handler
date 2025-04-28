#include "includeAll.lp".

%% two = 2
%% ten = 10

%% addtwoten = two+ten = 12
%% addtentwo = ten+two = 12
%% multtwoten = two*ten = 20
%% multtentwo = ten*two = 20
%% subtwoten = two-ten = -8
%% subtentwo = ten-two = 8
%% eqadds = addtwoten == addtentwo = true
%% neqmults = multtwoten != multtentwo = false
%% eqsubs = subtwoten == subtentwo = false
%% eqmsubs = -subtwoten == subtentwo = true
%% abssubtwoten = |subtwoten| = 8
%% abssubtentwo = |subtentwo| = 8
%% neqmtwoadds  =  -two != two = true
%% neqmmtwoadds = --two != two = false
%% leqtwoten = two <= ten = true
%% lttwoten  = two <  ten = true
%% geqtwoten = two >= ten = false
%% gttwoten  = two >  ten = false
%% leqatt = addtwoten <= addtentwo = true
%% ltatt  = addtwoten <  addtentwo = false
%% geqatt = addtwoten >= addtentwo = true
%% gtatt  = addtwoten >  addtentwo = false

assign(assign_x, x, constant(int(20))).
assign(assign_y, y, operation(add, (variable(x), (constant(int(10)), ())))).

assign(a_int, two, constant(int(2))).
assign(a_int, ten, constant(int(10))).

assign(a_int, addtwoten, operation(add,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, addtentwo, operation(add,(TEN,(TWO,())))) :-
    TWO = variable(two),
    TEN = variable(ten).

assign(a_int, multtwoten, operation(mult,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, multtentwo, operation(mult,(TEN,(TWO,())))) :-
    TWO = variable(two),
    TEN = variable(ten).

assign(a_int, subtwoten, operation(sub,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, subtentwo, operation(sub,(TEN,(TWO,())))) :-
    TWO = variable(two),
    TEN = variable(ten).

assign(a_int, eqadds, operation(eq,(TWOTEN,(TENTWO,())))) :-
    TWOTEN = variable(addtwoten),
    TENTWO = variable(addtentwo).
assign(a_int, neqmults, operation(neq,(TWOTEN,(TENTWO,())))) :-
    TWOTEN = variable(multtwoten),
    TENTWO = variable(multtentwo).
assign(a_int, eqsubs, operation(eq,(TWOTEN,(TENTWO,())))) :-
    TWOTEN  = variable(subtwoten),
    TENTWO  = variable(subtentwo).
assign(a_int, eqmsubs, operation(eq,(MTWOTEN,(TENTWO,())))) :-
    MTWOTEN = operation(minus,(TWOTEN,())),
    TWOTEN  = variable(subtwoten),
    TENTWO  = variable(subtentwo).

assign(a_int, abssubtwoten, operation(abs,(TWOTEN,()))) :-
    TWOTEN = variable(subtwoten).
assign(a_int, abssubtentwo, operation(abs,(TENTWO,()))) :-
    TENTWO = variable(subtentwo).

assign(a_int, neqmtwo, operation(neq,(MTWO,(TWO,())))) :-
    MTWO = operation(minus,(TWO,())),
    TWO = variable(two).
assign(a_int, neqmmtwo, operation(neq,(MMTWO,(TWO,())))) :-
    MMTWO = operation(minus,(MTWO,())),
    MTWO  = operation(minus,(TWO,())),
    TWO   = variable(two).

assign(a_int, leqtwoten, operation(leq,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, lttwoten, operation(lt,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, geqtwoten, operation(geq,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, gttwoten, operation(gt,(TWO,(TEN,())))) :-
    TWO = variable(two),
    TEN = variable(ten).
assign(a_int, leqatt, operation(leq,(TWO,(TEN,())))) :-
    TWO = variable(addtwoten),
    TEN = variable(addtentwo).
assign(a_int, ltatt, operation(lt,(TWO,(TEN,())))) :-
    TWO = variable(addtwoten),
    TEN = variable(addtentwo).
assign(a_int, geqatt, operation(geq,(TWO,(TEN,())))) :-
    TWO = variable(addtwoten),
    TEN = variable(addtentwo).
assign(a_int, gtatt, operation(gt,(TWO,(TEN,())))) :-
    TWO = variable(addtwoten),
    TEN = variable(addtentwo).
