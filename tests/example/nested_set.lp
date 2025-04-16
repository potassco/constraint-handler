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

%%% e = s1 == s2 and s2 == u and u == i = true
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

assign(assign_v1, v1, operation(add,(constant(int(1)),(constant(int(1)),())))).
assign(assign_v2, v2, constant(int(2))).
assign(assign_s1, s1, operation(makeSet,
                                   (variable(v1),()))).
assign(assign_s2, s2, operation(makeSet,
                                   (variable(v2),()))).
assign(assign_s3, s3, operation(makeSet,
                                   (constant(int(3)),()))).
assign(assign_s4, s4, operation(makeSet,
                                   (constant(int(4)),()))).
assign(assign_u, u, operation(union,
                                 (variable(s1),
                                 (variable(s2),())))).
assign(assign_i, i, operation(inter,
                                 (variable(s1),
                                 (variable(s2),())))).

assign(assign_ss1, ss1, operation(makeSet,
                                     (variable(s1),(variable(s3),())))).
assign(assign_ss2, ss2, operation(makeSet,
                                     (variable(s2),(variable(s4),())))).
assign(assign_ss3, ss3, operation(makeSet,
                                     (variable(s2),
                                     (operation(makeSet,(constant(int(3)),())),())))).
assign(assign_sa, sa, operation(makeSet,
                                   (variable(ss1),
                                   (variable(ss2),
                                   (variable(ss3),()))))).
assign(assign_su, su, operation(union,
                                   (variable(ss1),
                                   (variable(ss2),())))).
assign(assign_si, si, operation(inter,
                                   (variable(ss1),
                                   (variable(ss2),())))).

assign(assign_se, se, operation(union,
                                   (variable(ss1),
                                   (variable(ss1),())))).

assign(assign_e, e, operation(conj, (E12,(E2U,(EUI,()))))) :-
    E12 = operation(eq,(variable(s1),(variable(s2),()))),
    E2U = operation(eq,(variable(s2),(variable(u),()))),
    EUI = operation(eq,(variable(u),(variable(i),()))).
assign(a_lsa, lsa, operation(length,(variable(sa),()))).
assign(a_lsu, lsu, operation(length,(variable(su),()))).
assign(a_lsi, lsi, operation(length,(variable(si),()))).
assign(a_lse, lse, operation(length,(variable(se),()))).
assign(a_in4, in4e, operation(isin, (variable(s4),(variable(se),())))).
assign(a_in3, in3e, operation(isin, (variable(s3),(variable(se),())))).
assign(a_in2, in2e, operation(isin, (variable(s2),(variable(se),())))).
assign(a_nin4, notin4e, operation(notin, (variable(s4),(variable(se),())))).
assign(a_nin3, notin3e, operation(notin, (variable(s3),(variable(se),())))).
assign(a_nin2, notin2e, operation(notin, (variable(s2),(variable(se),())))).
