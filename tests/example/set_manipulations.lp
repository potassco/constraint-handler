#include "includeAll.lp".

%%% b = true
%%% i = 42
%%% f = 47.1
%%% s = { b, i+f } = { true, 89.1 }
%%% t = { 1, 2, 3, true }
%%% u = s cup t = { 1, 2, 3, true, 89.1 }
%%% v = s cap t = { true }
%%% w = { |u|, |v|, b in V, true not in u } = { 1, 5, true, false }
%%% cu = |u| = 5
%%% x = { 3, 1+2, u, v, { true } } = { 3, { true }, { 1, 2, 3, true, 89.1 } }
%%% cx = |x| = 3
%%% set d, d.add(1+3), d.add(s), d.add({true, 89.1}), d.add(2+2)  -> d = { 4, { true, 89.1 } }
%%% cd = 2

%%% numbers = { -2.0, -1, 0, 1, 2 }
%%% squares = { x*x | x \in numbers, x float or x int } = { 0, 1, 4, 4.0 }
%%% csquares = |squares| = 4

%%% eqx3 = x == { 3, { true }, { 1, 2, 3, true, 89.1 } } = true
%%% nqx3 = x != { 3, { true }, { 1, 2, 3, true, 89.1 } } = false
%%% eqx4 = x == { 3, { true }, { 1, 2, 4, true, 89.1 } } = false
%%% nqx4 = x != { 3, { true }, { 1, 2, 4, true, 89.1 } } = true

%%% tsubu = t subset u = true
%%% tsubv = t subset v = false
%%% tsubw = t subset w = false
%%% usubw = u subset w = false
%%% vsubw = v subset w = true
%%% usubx = u subset x = false
%%% vsubx = v subset x = false

%%% declare empty
%%% fold(+,empty,0) = 0

%%% TODO
%%% y = add f v = { 47.1 true }
%%% z = rem true  w = { 1, 5, false }
%%% a = rem false u = { 1, 2, 3, true, 89.1 } = u

assign(assign_b, b, val(bool,true)).
assign(assign_i, i, val(int,42)).
assign(assign_f, f, val(float,float("47.1"))).
assign(assign_s, s, operation(makeSet,
                                  (variable(b),
                                  (operation(add,(variable(i),(variable(f), ()))),())))).
assign(assign_t, t, operation(makeSet,
                                  (val(int,1),
                                  (val(int,2),
                                  (val(int,3),
                                  (val(bool,true),())))))).
assign(assign_u, u, operation(union,
                                  (variable(s),
                                  (variable(t),())))).
assign(assign_v, v, operation(inter,
                                  (variable(s),
                                  (variable(t),())))).

assign(assign_cu, cu, operation(length,(variable(u),()))).

assign(assign_w, w, operation(makeSet,
                                  (operation(length,(variable(u),())),
                                  (operation(length,(variable(v),())),
                                  (operation(isin,(variable(b),(variable(v),()))),
                                  (operation(notin,(val(bool,true),
                                                       (variable(u),()))),())))))).
assign(assign_x, x, operation(makeSet,
                                  (val(int,3),
                                  (operation(add,(val(int,1),(val(int,2),()))),
                                  (variable(u),
                                  (variable(v),
                                  (operation(makeSet,(val(bool,true),())),()))))))).

assign(assign_cx, cx, operation(length,(variable(x),()))).

set_declare(declare_d, d).
set_assign(assign_d, d, operation(add,(val(int,1),(val(int,3),())))).
set_assign(assign_d, d, variable(s)).
set_assign(assign_d, d, operation(add,(val(int,2),(val(int,2),())))).
set_assign(assign_d, d, operation(makeSet,(val(bool,true),(val(float,float("89.1")),())))).

assign(assign_cd, cd, operation(length,(variable(d),()))).

assign(a_numbers, numbers, operation(makeSet,
                                    (val(float,float("-2.0")),
                                    (val(int,-1),
                                    (val(int, 0),
                                    (val(int, 1),
                                    (val(int, 2),()))))))).

set_declare(d_squares,squares).
set_assign(a_squares, squares, SQ) :-
    set_value(numbers,T,X),
    SQ = operation(mult,(EX,(EX,()))),
    EX = val(T,X).

assign(a_csq, csquares, operation(length,(variable(squares),()))).

%%% eqx = x == { 3, { true }, { 1, 2, 3, true, 89.1 } } = true
%%% nqx = x == { 3, { true }, { 1, 2, 4, true, 89.1 } } = false
assign(tset_eq,eqx3,operation(eq,(variable(x),(X,())))) :-
    X=operation(makeSet,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(makeSet,(TRUE,())),
    SET=operation(makeSet,(ONE,(TWO,(THREE,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,1),
    TWO=val(int,2),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
assign(tset_eq,nqx3,operation(neq,(variable(x),(X,())))) :-
    X=operation(makeSet,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(makeSet,(TRUE,())),
    SET=operation(makeSet,(ONE,(TWO,(THREE,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,1),
    TWO=val(int,2),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
assign(tset_neq,eqx4,operation(eq,(variable(x),(X,())))) :-
    X=operation(makeSet,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(makeSet,(TRUE,())),
    SET=operation(makeSet,(ONE,(TWO,(FOUR,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,1),
    TWO=val(int,2),
    FOUR=val(int,4),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
assign(tset_neq,nqx4,operation(neq,(variable(x),(X,())))) :-
    X=operation(makeSet,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(makeSet,(TRUE,())),
    SET=operation(makeSet,(ONE,(TWO,(FOUR,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,1),
    TWO=val(int,2),
    FOUR=val(int,4),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).


assign(test_subset, tsubu, operation(subset,(variable(t),(variable(u),())))).
assign(test_subset, tsubv, operation(subset,(variable(t),(variable(v),())))).
assign(test_subset, tsubw, operation(subset,(variable(t),(variable(w),())))).
assign(test_subset, usubw, operation(subset,(variable(u),(variable(w),())))).
assign(test_subset, vsubw, operation(subset,(variable(v),(variable(w),())))).
assign(test_subset, usubx, operation(subset,(variable(u),(variable(x),())))).
assign(test_subset, vsubx, operation(subset,(variable(v),(variable(x),())))).

set_declare(d_empty,empty).
evaluate(fold,(val(function,plus),(variable(empty),(val(int,0),())))).
