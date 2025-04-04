#include "includeAll.lp".

%%% b = true
%%% i = 42
%%% f = 47.1
%%% s = { b, i+f } = { true, 89.1 }
%%% t = { 1, 2, 3, true }
%%% u = s cup t = { 1, 2, 3, true, 89.1 }
%%% v = s cap t = { true }
%%% w = { |u|, |v|, b in V, true not in u } = { 1, 5, true, false }
%%% x = { 3, 1+2, u, v, { true } } = { 3, { true }, { 1, 2, 3, true, 89.1 } }
%%% y = add f v = { 47.1 true }
%%% z = rem true  w = { 1, 5, false }
%%% a = rem false u = { 1, 2, 3, true, 89.1 } = u

assign(assign_b, b, constant(bool(true))).
assign(assign_i, i, constant(int(42))).
assign(assign_f, f, constant(float("47.1"))).
assign(assign_s, s, operation(makeSet,
                                  (variable(b),
                                  (operation(add,(variable(i),(variable(f), ()))),())))).
assign(assign_t, t, operation(makeSet,
                                  (constant(int(1)),
                                  (constant(int(2)),
                                  (constant(int(3)),
                                  (constant(bool(true)),())))))).
assign(assign_u, u, operation(union,
                                  (variable(s),
                                  (variable(t),())))).
assign(assign_v, v, operation(inter,
                                  (variable(s),
                                  (variable(t),())))).

assign(assign_w, w, operation(makeSet,
                                  (operation(length,(variable(u),())),
                                  (operation(length,(variable(v),())),
                                  (operation(isin,(variable(b),(variable(v),()))),
                                  (operation(notin,(constant(bool(true)),
                                                       (variable(u),()))),())))))).

assign(assign_x, x, operation(makeSet,
                                  (constant(int(3)),
                                  (operation(add,(constant(int(1)),(constant(int(2)),()))),
                                  (variable(u),
                                  (variable(v),
                                  (operation(makeSet,(constant(bool(true)),())),()))))))).

%assign(assign_y, y, operation(add,
%                                  (variable(f),
%                                  (variable(v),())))).
%assign(assign_z, z, operation(rem,
%                                  (constant(bool(true)),
%                                  (variable(w),())))).
%assign(assign_a, a, operation(rem,
%                                  (constant(bool(false)),
%                                  (variable(u),())))).

requestEngine(assign_x,compile).

%#show expression/1.
