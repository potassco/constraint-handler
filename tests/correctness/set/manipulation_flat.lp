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
%%% true set_isin t    not (17 set_isin t)

%%% tsubu = t subset u = true
%%% tsubv = t subset v = false
%%% tsubw = t subset w = false
%%% usubw = u subset w = false
%%% vsubw = v subset w = true

%%% vp = { 5, 6, 7 } cap { 7, 8, 9 } = { 7 }

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

variable_define(duv,operation(diff,
                                  (variable(u),
                                  (variable(v),())))).

variable_define(cduv,operation(length,(variable(duv),()))).
variable_define(cu,operation(length,(variable(u),()))).

variable_define(w,operation(set_make,
                                  (operation(length,(variable(u),())),
                                  (operation(add,(operation(length,(variable(v),())),(val(int,1),()))),
                                  (operation(set_isin,(variable(b),(variable(v),()))),
                                  (operation(set_notin,(val(bool,true),
                                                       (variable(u),()))),())))))).

evaluate(set_isin,(val(bool,true),(variable(t),()))).
evaluate(set_isin,(val(int,17),(variable(t),()))).


variable_define(tsubu,operation(subset,(variable(t),(variable(u),())))).
variable_define(tsubv,operation(subset,(variable(t),(variable(v),())))).
variable_define(tsubw,operation(subset,(variable(t),(variable(w),())))).
variable_define(usubw,operation(subset,(variable(u),(variable(w),())))).
variable_define(vsubw,operation(subset,(variable(v),(variable(w),())))).

variable_define(vp,operation(inter,
                            (operation(set_make,(val(int,5),(val(int,6),(val(int,7),())))),
                            (operation(set_make,(val(int,7),(val(int,8),(val(int,9),())))),())))).
