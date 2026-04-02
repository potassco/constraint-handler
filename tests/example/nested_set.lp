%%% v1 = 1 + 1
%%% v2 = 2
%%% s1 = { v1 } = { 2 }
%%% s2 = { v2 } = { 2 }
%%% s3 = { 3 }
%%% s4 = { 4 }
%%% u = s1 cup s2 = { 2 }
%%% i = s1 cap s2 = { 2 }
%%% ss1 = { s1, s3 } = { { 2 }, { 3 } }
%%% ss2 = { s2, s4 } = { { 2 }, { 4 } }
%%% ss3 = { s2, { 3 } } = { { 2 }, { 3 } }
%%% sa = { ss1, ss2, ss3 } = { { { 2 }, { 3 } }, { { 2 }, { 4 } } }
%%% su = ss1 cup ss2 = { { 2 }, { 3 }, { 4 } }
%%% si = ss1 cap ss2 = { { 2 } }
%%% se = ss1 cup ss1 = { { 2 }, { 3 } }

%%% e = s1 == s2 and s2 == u and u == i and s1 != s4 = true
%%% n = s1 != s2 or  s2 != u or  u != i or  s1 == s4 = false
%%% lsa = |sa| = 2
%%% lsu = |su| = 3
%%% lsi = |si| = 1
%%% lse = |se| = 2
%%% in4e = s4 \in se = false
%%% in3e = s3 \in se = true
%%% in2e = s2 \in se = true
%%% set_notin4 = s4 \set_notin se = true
%%% set_notin3 = s3 \set_notin se = false
%%% set_notin2 = s2 \set_notin se = false

variable_define(v1, operation(add,(val(int,1),(val(int,1),())))).
variable_define(v2, val(int,2)).
variable_define(s1, operation(set_make,
                                   (variable(v1),()))).
variable_define(s2, operation(set_make,
                                   (variable(v2),()))).
variable_define(s3, operation(set_make,
                                   (val(int,3),()))).
variable_define(s4, operation(set_make,
                                   (val(int,4),()))).
variable_define(u, operation(union,
                                 (variable(s1),
                                 (variable(s2),())))).
variable_define(i, operation(inter,
                                 (variable(s1),
                                 (variable(s2),())))).

variable_define(ss1, operation(set_make,
                                     (variable(s1),(variable(s3),())))).
variable_define(ss2, operation(set_make,
                                     (variable(s2),(variable(s4),())))).
variable_define(ss3, operation(set_make,
                                     (variable(s2),
                                     (operation(set_make,(val(int,3),())),())))).
variable_define(sa, operation(set_make,
                                   (variable(ss1),
                                   (variable(ss2),
                                   (variable(ss3),()))))).
variable_define(su, operation(union,
                                   (variable(ss1),
                                   (variable(ss2),())))).
variable_define(si, operation(inter,
                                   (variable(ss1),
                                   (variable(ss2),())))).

variable_define(se, operation(union,
                                   (variable(ss1),
                                   (variable(ss1),())))).

variable_define(e, operation(conj, (E12,(E2U,(EUI,(N14,())))))) :-
    E12 = operation(eq,(variable(s1),(variable(s2),()))),
    E2U = operation(eq,(variable(s2),(variable(u),()))),
    EUI = operation(eq,(variable(u),(variable(i),()))),
    N14 = operation(neq,(variable(s1),(variable(s4),()))).
variable_define(n, operation(disj, (N12,(N2U,(NUI,(E14,())))))) :-
    N12 = operation(neq,(variable(s1),(variable(s2),()))),
    N2U = operation(neq,(variable(s2),(variable(u),()))),
    NUI = operation(neq,(variable(u),(variable(i),()))),
    E14 = operation(eq,(variable(s1),(variable(s4),()))).
variable_define(lsa, operation(length,(variable(sa),()))).
variable_define(lsu, operation(length,(variable(su),()))).
variable_define(lsi, operation(length,(variable(si),()))).
variable_define(lse, operation(length,(variable(se),()))).
variable_define(in4e, operation(set_isin, (variable(s4),(variable(se),())))).
variable_define(in3e, operation(set_isin, (variable(s3),(variable(se),())))).
variable_define(in2e, operation(set_isin, (variable(s2),(variable(se),())))).
variable_define(set_notin4e, operation(set_notin, (variable(s4),(variable(se),())))).
variable_define(set_notin3e, operation(set_notin, (variable(s3),(variable(se),())))).
variable_define(set_notin2e, operation(set_notin, (variable(s2),(variable(se),())))).
