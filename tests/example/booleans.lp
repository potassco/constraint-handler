#include "includeAll.lp".

%% x = true or false
%% y = true or false

%% f = (x | y) & (-x | -y) & (-x | y)
%% g = f -> x
%% h = f <-> x & -y
%% t = x xor y
%% z = if x then y else -y
%% w = z == (x <-> y)
%% v = z != t
%% u = f -> y
%% n = (f -> y) & f

1 { assign(a_x, x, constant(bool(false)),()) ; assign(a_x, x, constant(bool(true)),()) } 1.
1 { assign(a_y, y, constant(bool(false)),()) ; assign(a_y, y, constant(bool(true)),()) } 1.
assign(a_f, f, operation(conj, (PXPY, (NXNY, (NXPY, ()))))) :-
    PXPY = operation(disj, (PX, (PY, ()))),
    NXNY = operation(disj, (NX, (NY, ()))),
    NXPY = operation(disj, (NX, (PY, ()))),
    PX = variable(x),
    PY = variable(y),
    NX = operator(lnot,(PX,())),
    NY = operator(lnot,(PY,())).

assign(a_g, g, operation(limp, (F, (PX, ())))) :-
    F = variable(f),
    PX = variable(x).

assign(a_h, h, operation(leqv, (F, (PXNY, ())))) :-
    F = variable(f),
    PX = variable(x),
    PY = variable(y),
    NY = operator(lnot,(PY,())),
    PXNY = operation(conj, (PX, (NY, ()))).
assign(a_t, t, operation(disj, (PX, (PY, ())))) :-
    PX = variable(x),
    PY = variable(y).
assign(a_z, z, operation(ite, (PX, (PY, (NY, ()))))) :-
    PX = variable(x),
    PY = variable(y),
    NY = operator(lnot,(PY,())).
assign(a_w, w, operation(eq, (PZ, (PXPY, ())))) :-
    PZ = variable(z),
    PX = variable(x),
    PY = variable(y),
    PXPY = operator(leqv,(PX, (PY,()))).
assign(a_v, v, operation(neq, (PZ, (PT, ())))) :-
    PZ = variable(z),
    PT = variable(t).
assign(a_u, u, operation(limp, (F, (PY, ())))) :-
    F = variable(f),
    PY = variable(y).

assign(a_n, n, operation(conj, (FPY, (F, ())))) :-
    FPY = operation(limp, (F, (PY, ()))),
    F = variable(f),
    PY = variable(y).
