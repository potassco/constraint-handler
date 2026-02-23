%%% b = true
%%% i = 42
%%% f = 47.1
%%% s = { b, i+f } = { true, 89.1 }
%%% t = { 10, 2, 3, true }
%%% u = s cup t = { 10, 2, 3, true, 89.1 }
%%% v = s cap t = { true }
%%% duv = u \\ v = { 10, 2, 3, 89.1 }
%%% cduv = |duv| = 4
%%% w = { |u|+1, |v|, b in V, true not in u } = { Z, 5, true, false }
%%% cu = |u| = 5
%%% x = { 3, 1+2, u, v, { true } } = { 3, { true }, { 10, 2, 3, true, 89.1 } }
%%% cx = |x| = 3
%%% set d, d.add(1+3), d.add(s), d.add({true, 89.1}), d.add(2+2)  -> d = { 4, { true, 89.1 } }
%%% cd = 2
%%% true notin d      true notin x     true isin t

%%% eqx3 = x == { 3, { true }, { 10, 2, 3, true, 89.1 } } = true
%%% nqx3 = x != { 3, { true }, { 10, 2, 3, true, 89.1 } } = false
%%% eqx4 = x == { 3, { true }, { 10, 2, 4, true, 89.1 } } = false
%%% nqx4 = x != { 3, { true }, { 10, 2, 4, true, 89.1 } } = true

%%% tsubu = t subset u = true
%%% tsubv = t subset v = false
%%% tsubw = t subset w = false
%%% usubw = u subset w = false
%%% vsubw = v subset w = true
%%% usubx = u subset x = false
%%% vsubx = v subset x = false

%%% vp = { 5, 6, 7 } cap { 7, 8, 9 } = { 7 }

%%% TODO
%%% y = add f v = { 47.1 true }
%%% z = rem true  w = { 1, 5, false }
%%% a = rem false u = { 1, 2, 3, true, 89.1 } = u

variable_define(assign_b, b, val(bool,true)).
variable_define(assign_i, i, val(int,42)).
variable_define(assign_f, f, val(float,float("47.1"))).
variable_define(assign_s, s, operation(set_make,
                                  (variable(b),
                                  (operation(add,(variable(i),(variable(f), ()))),())))).
variable_define(assign_t, t, operation(set_make,
                                  (val(int,10),
                                  (val(int,2),
                                  (val(int,3),
                                  (val(bool,true),())))))).
variable_define(assign_u, u, operation(union,
                                  (variable(s),
                                  (variable(t),())))).
variable_define(assign_v, v, operation(inter,
                                  (variable(s),
                                  (variable(t),())))).

variable_define(assign_duv, duv, operation(diff,
                                  (variable(u),
                                  (variable(v),())))).

variable_define(assign_cduv, cduv, operation(length,(variable(duv),()))).

variable_define(assign_cu, cu, operation(length,(variable(u),()))).

variable_define(assign_w, w, operation(set_make,
                                  (operation(length,(variable(u),())),
                                  (operation(add,(operation(length,(variable(v),())),(val(int,1),()))),
                                  (operation(isin,(variable(b),(variable(v),()))),
                                  (operation(notin,(val(bool,true),
                                                       (variable(u),()))),())))))).
variable_define(assign_x, x, operation(set_make,
                                  (val(int,3),
                                  (operation(add,(val(int,1),(val(int,2),()))),
                                  (variable(u),
                                  (variable(v),
                                  (operation(set_make,(val(bool,true),())),()))))))).

variable_define(assign_cx, cx, operation(length,(variable(x),()))).

set_declare(declare_d, d).
set_assign(assign_d, d, operation(add,(val(int,1),(val(int,3),())))).
set_assign(assign_d, d, variable(s)).
set_assign(assign_d, d, operation(add,(val(int,2),(val(int,2),())))).
set_assign(assign_d, d, operation(set_make,(val(bool,true),(val(float,float("89.1")),())))).

variable_define(assign_cd, cd, operation(length,(variable(d),()))).

evaluate(notin,(val(bool,true),(variable(d),()))).
evaluate(notin,(val(bool,true),(variable(x),()))).
evaluate(isin,(val(bool,true),(variable(t),()))).
evaluate(isin,(val(int,17),(variable(t),()))).

%%% eqx = x == { 3, { true }, { 10, 2, 3, true, 89.1 } } = true
%%% nqx = x == { 3, { true }, { 10, 2, 4, true, 89.1 } } = false
variable_define(tset_eq,eqx3,operation(eq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(THREE,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
variable_define(tset_eq,nqx3,operation(neq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(THREE,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
variable_define(tset_neq,eqx4,operation(eq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(FOUR,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    FOUR=val(int,4),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
variable_define(tset_neq,nqx4,operation(neq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(FOUR,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    FOUR=val(int,4),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).


variable_define(test_subset, tsubu, operation(subset,(variable(t),(variable(u),())))).
variable_define(test_subset, tsubv, operation(subset,(variable(t),(variable(v),())))).
variable_define(test_subset, tsubw, operation(subset,(variable(t),(variable(w),())))).
variable_define(test_subset, usubw, operation(subset,(variable(u),(variable(w),())))).
variable_define(test_subset, vsubw, operation(subset,(variable(v),(variable(w),())))).
variable_define(test_subset, usubx, operation(subset,(variable(u),(variable(x),())))).
variable_define(test_subset, vsubx, operation(subset,(variable(v),(variable(x),())))).

variable_define(assign_vp, vp, operation(inter,
                                  (operation(set_make,(val(int,5),(val(int,6),(val(int,7),())))),
                                  (operation(set_make,(val(int,7),(val(int,8),(val(int,9),())))),())))).
