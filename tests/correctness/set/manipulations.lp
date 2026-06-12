%%% b = true
%%% i = 42
%%% f = 47.1
%%% s = { b, i+f } = { true, 89.1 }
%%% t = { 10, 2, 3, true }
%%% u = s cup t = { 10, 2, 3, true, 89.1 }
%%% v = s cap t = { true }
%%% duv = u \\ v = { 10, 2, 3, 89.1 }
%%% w = { |u|+1, |v|, b in V, true not in u } = { Z, 5, true, false }
%%% cu = |u| = 5
%%% x = { 3, 1+2, u, v, { true } } = { 3, { true }, { 10, 2, 3, true, 89.1 } }
%%% cx = |x| = 3
%%% set d, d.add(1+3), d.add(s), d.add({true, 89.1}), d.add(2+2)  -> d = { 4, { true, 89.1 } }
%%% cd = 2
%%% true set_notin d      true set_notin x

%%% eqx3 = x == { 3, { true }, { 10, 2, 3, true, 89.1 } } = true
%%% nqx3 = x != { 3, { true }, { 10, 2, 3, true, 89.1 } } = false
%%% eqx4 = x == { 3, { true }, { 10, 2, 4, true, 89.1 } } = false
%%% nqx4 = x != { 3, { true }, { 10, 2, 4, true, 89.1 } } = true

%%% usubx = u subset x = false
%%% vsubx = v subset x = false

variable_define(b,val(bool,true)).
variable_define(i,val(int,42)).
variable_define(f,val(float,float("47.1"))).
variable_define(s,operation(set_make,
                                  (variable(b),
                                  (operation(add,(variable(i),(variable(f), ()))),())))).
variable_define(t,operation(set_make,
                                  (val(int,10),
                                  (val(int,2),
                                  (val(int,3),
                                  (val(bool,true),())))))).
variable_define(u,operation(union,
                                  (variable(s),
                                  (variable(t),())))).
variable_define(v,operation(inter,
                                  (variable(s),
                                  (variable(t),())))).

variable_define(x,operation(set_make,
                                  (val(int,3),
                                  (operation(add,(val(int,1),(val(int,2),()))),
                                  (variable(u),
                                  (variable(v),
                                  (operation(set_make,(val(bool,true),())),()))))))).

variable_define(cx, operation(length,(variable(x),()))).

variable_declare(d,set).
set_assign(d,operation(add,(val(int,1),(val(int,3),())))).
set_assign(d,variable(s)).
set_assign(d,operation(add,(val(int,2),(val(int,2),())))).
set_assign(d,operation(set_make,(val(bool,true),(val(float,float("89.1")),())))).

variable_define(cd,operation(length,(variable(d),()))).

evaluate(set_notin,(val(bool,true),(variable(d),()))).
evaluate(set_notin,(val(bool,true),(variable(x),()))).

%%% eqx = x == { 3, { true }, { 10, 2, 3, true, 89.1 } } = true
%%% nqx = x == { 3, { true }, { 10, 2, 4, true, 89.1 } } = false
variable_define(eqx3,operation(eq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(THREE,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
variable_define(nqx3,operation(neq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(THREE,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
variable_define(eqx4,operation(eq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(FOUR,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    FOUR=val(int,4),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).
variable_define(nqx4,operation(neq,(variable(x),(X,())))) :-
    X=operation(set_make,(THREE,(STRUE,(SET,())))),
    THREE=val(int,3),
    STRUE=operation(set_make,(TRUE,())),
    SET=operation(set_make,(ONE,(TWO,(FOUR,(TRUE,(EIGHTYNINE,())))))),
    ONE=val(int,10),
    TWO=val(int,2),
    FOUR=val(int,4),
    TRUE=val(bool,true),
    EIGHTYNINE=val(float,float("89.1")).


variable_define(usubx,operation(subset,(variable(u),(variable(x),())))).
variable_define(vsubx,operation(subset,(variable(v),(variable(x),())))).
