%%% a = {a} = { { a } } = { { { a } } } = ...
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


set_declare(a).
set_assign(a,variable(a)).
set_declare(b).
set_assign(b,variable(b)).
set_declare(c).
set_assign(c,variable(c)).
set_declare(d).
set_assign(d,variable(a)).
set_assign(d,variable(b)).
set_declare(e).
set_assign(e,SSA) :-
    SSA = operation(set_make,(SA,())),
    SA = operation(set_make,(A,())),
    A = variable(a).
set_declare(f).
set_assign(f,variable(f)).
set_assign(f,val(int,1)).
set_declare(g).
set_assign(g,variable(g)).
set_assign(g,val(int,1)).
set_assign(g,val(int,2)).
set_declare(h).
set_assign(h,variable(f)).
set_assign(h,val(int,1)).
set_assign(h,val(int,2)).
set_declare(i).
set_assign(i,variable(i)).
set_assign(i,val(int,1)).
set_assign(i,val(int,2)).

set_declare(nb).
set_assign(nb,val(int,0..10)).

set_declare(even).
set_assign(even,val(int,0)).
set_assign(even,EX) :-
    EX = val(int,X),
    set_value(nb,EX),
    set_value(odd,val(int,X-1)).

set_declare(odd).
set_assign(odd,EX) :-
    EX = val(int,X),
    set_value(nb,EX),
    set_value(even,val(int,X-1)).

set_declare(doubles).
set_assign(doubles,TWOX) :-
    TWO = val(int,2),
    EX = val(int,X),
    TWOX = operation(mult,(TWO,(EX,()))),
    set_value(nb,EX).

set_declare(es).
set_assign(es,EX) :-
    EX = val(int,X),
    set_value(nb,EX),
    not set_value(os,EX).

set_declare(os).
set_assign(os,EX) :-
    EX = val(int,X),
    set_value(nb,EX),
    set_value(es,val(int,X-1)).

%%% any:
evaluate(eq,(variable(a),(variable(b),()))).
evaluate(eq,(variable(a),(variable(c),()))).
evaluate(eq,(variable(b),(variable(c),()))).
evaluate(eq,(variable(es),(variable(even),()))).
evaluate(eq,(variable(os),(variable(odd),()))).

%%% all:
evaluate(eq,(variable(a),(variable(a),()))).
evaluate(eq,(variable(e),(variable(a),()))).
evaluate(leqv,
    (operation(eq,(variable(a),(variable(b),()))),
    (operation(eq,(variable(b),(variable(a),()))),()))).
evaluate(limp,
    (operation(conj,
        (operation(eq,(variable(a),(variable(b),()))),
        (operation(eq,(variable(a),(variable(c),()))),()))),
    (operation(eq,(variable(b),(variable(c),()))),()))).
evaluate(leqv,
    (operation(eq,(variable(d),(variable(a),()))),
    (operation(eq,(variable(b),(variable(a),()))),()))).
evaluate(subset,(variable(a),(variable(d),()))).
evaluate(subset,(variable(f),(variable(g),()))).
evaluate(subset,(variable(f),(variable(h),()))).
evaluate(notin,(val(int,6),(variable(odd),()))).
evaluate(isin,(val(int,7),(variable(odd),()))).
%%% even==doubles cap nb
evaluate(eq,
    (variable(even),
    (operation(inter,(variable(doubles),(variable(nb),()))),()))).
