#include "includeAll.lp".

%% x = "foo" or "bar"
%% y = "bla" or "bar" or "foobar"

%% f = x == y
%% g = x != y
%% h = f != g
%% i = |x|
%% t = y + x == "barfoo" | |y| == |x| | y == "foobar" | y + y == "blabla"

1 { assign(a_x, x, constant(str("foo"))) ; assign(a_x, x, constant(str("bar"))) } 1.
1 { assign(a_y, y, constant(str("bla"))) ; assign(a_y, y, constant(str("bar"))) ; assign(a_y, y, constant(str("foobar"))) } 1.
assign(a_f, f, operation(eq, (X, (Y, ())))) :-
    X = variable(x),
    Y = variable(y).

assign(a_g, g, operation(neq, (X, (Y, ())))) :-
    X = variable(x),
    Y = variable(y).

assign(a_h, h, operation(neq, (F, (G, ())))) :-
    F = variable(f),
    G = variable(g).

assign(a_i, i, operation(length, (X, ()))) :-
    X = variable(x).

assign(a_t, t, operation(disj, (YXBF, (XY, (YFB, (YYBB,())))))) :-
%assign(a_t, t, XY) :-
%assign(a_t, t, operation(or, (XY, (REST, ())))) :-
    X = variable(x),
    Y = variable(y),
    YX = operation(add,(Y,(X,()))),
    BF = constant(str("barfoo")),
    YXBF = operation(eq,(YX,(BF,()))),
    XY = operation(eq,(X,(Y,()))),
    FB = constant(str("foobar")),
    YFB = operation(eq,(Y,(FB,()))),
    YY = operation(add,(Y,(Y,()))),
    BB = constant(str("blabla")),
    YYBB = operation(eq,(YY,(BB,()))),
    REST = operation(or, (YFB, (YYBB,()))).

assign(a_yy, yy, operation(add, (Y, (Y, ())))) :-
    Y = variable(y).
