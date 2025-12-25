#include "includeAll.lp".

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
%%% notin4 = s4 \notin se = true
%%% notin3 = s3 \notin se = false
%%% notin2 = s2 \notin se = false

variable_define(assign_v1, v1, operation(add,(val(int,1),(val(int,1),())))).
variable_define(assign_v2, v2, val(int,2)).
variable_define(assign_s1, s1, operation(makeSet,
                                   (variable(v1),()))).
variable_define(assign_s2, s2, operation(makeSet,
                                   (variable(v2),()))).
variable_define(assign_s3, s3, operation(makeSet,
                                   (val(int,3),()))).
variable_define(assign_s4, s4, operation(makeSet,
                                   (val(int,4),()))).
variable_define(assign_u, u, operation(union,
                                 (variable(s1),
                                 (variable(s2),())))).
variable_define(assign_i, i, operation(inter,
                                 (variable(s1),
                                 (variable(s2),())))).

variable_define(assign_ss1, ss1, operation(makeSet,
                                     (variable(s1),(variable(s3),())))).
variable_define(assign_ss2, ss2, operation(makeSet,
                                     (variable(s2),(variable(s4),())))).
variable_define(assign_ss3, ss3, operation(makeSet,
                                     (variable(s2),
                                     (operation(makeSet,(val(int,3),())),())))).
variable_define(assign_sa, sa, operation(makeSet,
                                   (variable(ss1),
                                   (variable(ss2),
                                   (variable(ss3),()))))).
variable_define(assign_su, su, operation(union,
                                   (variable(ss1),
                                   (variable(ss2),())))).
variable_define(assign_si, si, operation(inter,
                                   (variable(ss1),
                                   (variable(ss2),())))).

variable_define(assign_se, se, operation(union,
                                   (variable(ss1),
                                   (variable(ss1),())))).

variable_define(assign_e, e, operation(conj, (E12,(E2U,(EUI,(N14,())))))) :-
    E12 = operation(eq,(variable(s1),(variable(s2),()))),
    E2U = operation(eq,(variable(s2),(variable(u),()))),
    EUI = operation(eq,(variable(u),(variable(i),()))),
    N14 = operation(neq,(variable(s1),(variable(s4),()))).
variable_define(assign_n, n, operation(disj, (N12,(N2U,(NUI,(E14,())))))) :-
    N12 = operation(neq,(variable(s1),(variable(s2),()))),
    N2U = operation(neq,(variable(s2),(variable(u),()))),
    NUI = operation(neq,(variable(u),(variable(i),()))),
    E14 = operation(eq,(variable(s1),(variable(s4),()))).
variable_define(a_lsa, lsa, operation(length,(variable(sa),()))).
variable_define(a_lsu, lsu, operation(length,(variable(su),()))).
variable_define(a_lsi, lsi, operation(length,(variable(si),()))).
variable_define(a_lse, lse, operation(length,(variable(se),()))).
variable_define(a_in4, in4e, operation(isin, (variable(s4),(variable(se),())))).
variable_define(a_in3, in3e, operation(isin, (variable(s3),(variable(se),())))).
variable_define(a_in2, in2e, operation(isin, (variable(s2),(variable(se),())))).
variable_define(a_nin4, notin4e, operation(notin, (variable(s4),(variable(se),())))).
variable_define(a_nin3, notin3e, operation(notin, (variable(s3),(variable(se),())))).
variable_define(a_nin2, notin2e, operation(notin, (variable(s2),(variable(se),())))).
