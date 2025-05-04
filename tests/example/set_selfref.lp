#include "includeAll.lp".

%%% a = {a}
%%% b = {b}
%%% c = {c}
%%% d = {a,b}
%%% e = {{{a}}}
%%% f = {1,f}
%%% g = {1,2,g}
%%% h = {1,2,f}
%%% nb = { 0,1,...,10 }
%%% even = { 0 } cup { x | x in nb, x-1 in odd  } = { 0,2,4, ...,10 }
%%% odd  =           { x | x in nb, x-1 in even } = { 1,3,5, ...,9 }
%%% doubles = { 2x | x in nb }
%%% es = nb \ os = { 0,2,4, ...,10 }
%%% os = { x | x in nb, x-1 in es } = { 1,3,5, ...,9 }

%%% any:
%%% a==b     a!=b     a==c     a!=c     b==c     b!=c

%%% all:
%%% a==a     e==a     a==b<->b==a
%%% a==b & a==c -> b==c
%%% d==a <-> b==a
%%% a subset d
%%% not (f subset g)
%%% f subset h
%%% es==even     os==odd
%%% even==doubles cap nb
%%% 6 notin odd
%%% 7 in odd


set_declare(set_selfref,a).
set_assign(set_selfref,a,variable(a)).
set_declare(set_selfref,b).
set_assign(set_selfref,b,variable(b)).
set_declare(set_selfref,c).
set_assign(set_selfref,c,variable(c)).
set_declare(set_selfref,d).
set_assign(set_selfref,d,variable(a)).
set_assign(set_selfref,d,variable(b)).
set_declare(set_selfref,e).
set_assign(set_selfref,e,SSA) :-
    SSA = operation(makeSet,(SA,())),
    SA = operation(makeSet,(A,())),
    A = variable(a).
set_declare(set_selfref,f).
set_assign(set_selfref,f,variable(f)).
set_assign(set_selfref,f,constant(int(1))).
set_declare(set_selfref,g).
set_assign(set_selfref,g,variable(g)).
set_assign(set_selfref,g,constant(int(1))).
set_assign(set_selfref,g,constant(int(2))).
set_declare(set_selfref,h).
set_assign(set_selfref,h,variable(f)).
set_assign(set_selfref,h,constant(int(1))).
set_assign(set_selfref,h,constant(int(2))).
set_declare(set_selfref,i).
set_assign(set_selfref,i,variable(i)).
set_assign(set_selfref,i,constant(int(1))).
set_assign(set_selfref,i,constant(int(2))).

set_declare(set_selfref,nb).
set_assign(set_selfref,nb,constant(int(0..10))).

set_declare(set_selfref,even).
set_assign(set_selfref,even,constant(int(0))).
set_assign(set_selfref,even,EX) :-
    EX = constant(int(X)),
    set_value(nb,int,X),
    set_value(odd,int,X-1).

set_declare(set_selfref,odd).
set_assign(set_selfref,odd,EX) :-
    EX = constant(int(X)),
    set_value(nb,int,X),
    set_value(even,int,X-1).

set_declare(set_selfref,doubles).
set_assign(set_selfref,doubles,TWOX) :-
    TWO = constant(int(2)),
    EX = constant(int(X)),
    TWOX = operation(mult,(TWO,(EX,()))),
    set_value(nb,int,X).

set_declare(set_selfref,es).
set_assign(set_selfref,es,EX) :-
    EX = constant(int(X)),
    set_value(nb,int,X),
    not set_value(os,int,X).

set_declare(set_selfref,os).
set_assign(set_selfref,os,EX) :-
    EX = constant(int(X)),
    set_value(nb,int,X),
    set_value(es,int,X-1).

%%% any:
evaluate(set_selfref,operation(eq,(variable(a),(variable(b),())))).
evaluate(set_selfref,operation(eq,(variable(a),(variable(c),())))).
evaluate(set_selfref,operation(eq,(variable(b),(variable(c),())))).
evaluate(set_selfref,operation(eq,(variable(es),(variable(even),())))).
evaluate(set_selfref,operation(eq,(variable(os),(variable(odd),())))).

%%% all:
evaluate(set_selfref,operation(eq,(variable(a),(variable(a),())))).
evaluate(set_selfref,operation(eq,(variable(e),(variable(a),())))).
evaluate(set_selfref,operation(leqv,
    (operation(eq,(variable(a),(variable(b),()))),
    (operation(eq,(variable(b),(variable(a),()))),())))).
evaluate(set_selfref,operation(limp,
    (operation(conj,
        (operation(eq,(variable(a),(variable(b),()))),
        (operation(eq,(variable(a),(variable(c),()))),()))),
    (operation(eq,(variable(b),(variable(c),()))),())))).
evaluate(set_selfref,operation(leqv,
    (operation(eq,(variable(d),(variable(a),()))),
    (operation(eq,(variable(b),(variable(a),()))),())))).
evaluate(set_selfref,operation(subset,(variable(a),(variable(d),())))).
evaluate(set_selfref,operation(subset,(variable(f),(variable(g),())))).
evaluate(set_selfref,operation(subset,(variable(f),(variable(h),())))).
evaluate(set_selfref,operation(notin,(constant(int(6)),(variable(odd),())))).
evaluate(set_selfref,operation(isin,(constant(int(7)),(variable(odd),())))).
%%% even==doubles cap nb
evaluate(set_selfref,operation(eq,
    (variable(even),
    (operation(inter,(variable(doubles),(variable(nb),()))),())))).
