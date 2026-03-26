%%% a = { { 1, 2 } : { 2, 4};
%%%       { 2, 4 } : { 4, 8 }, { 1, 2 }  }
%%% b = { { 1, 2 } : { 1+1, 2+2 };
%%%       b24 : { 1+1, 1 }, b48 }
%%%     where b24 = { 2 * 1, 2 * 2 } and b48 = { 4, 8 }
%%% c = { { 1, 2 } : { 2, 4}; { 2, 4 } : { 4, 7 }, { 1, 2 } }
%%% d = { { 1, 2 } : { 2, 4}; { 2, 4 } : { 4, 8 } }
%%% e = { { 1, 2 } : { 2, 4} }

%%% All:
%%% a==b     not a==c     not a==d     not a==e     not a!=b     a!=c     a!=d     a!=e
%%% d!=e     e!=d

variable_define(aa, a, operation(multimap_make,
                       ((operation(set_make,(val(int,1),(val(int,2),()))),operation(set_make,(val(int,2),(val(int,4),())))),
                       ((operation(set_make,(val(int,2),(val(int,4),()))),operation(set_make,(val(int,4),(val(int,8),())))),
                       ((operation(set_make,(val(int,2),(val(int,4),()))),operation(set_make,(val(int,1),(val(int,2),())))),
                       ()))))).

multimap_declare(ab,b).
multimap_assign(ab,b,
    operation(set_make,(val(int,1),(val(int,2),()))),
    operation(set_make,
             (operation(add,(val(int,1),(val(int,1),()))),
             (operation(add,(val(int,2),(val(int,2),()))),())))).

variable_define(abs,b24,
    operation(set_make,
        (operation(mult,(val(int,2),(val(int,1),()))),
        (operation(mult,(val(int,2),(val(int,2),()))),())))).
multimap_assign(ab,b,
    variable(b24),
    operation(set_make,
             (operation(add,(val(int,1),(val(int,1),()))),
             (val(int,1),
             ())))).

set_declare(dbs,b48).
set_assign(abs,b48,val(int,4)).
set_assign(abs,b48,val(int,8)).

multimap_assign(ab,b,
    variable(b24),
    variable(b48)).

variable_define(ac, c, operation(multimap_make,
                       ((operation(set_make,(val(int,1),(val(int,2),()))), operation(set_make,(val(int,2),(val(int,4),())))),
                       ((operation(set_make,(val(int,2),(val(int,4),()))), operation(set_make,(val(int,4),(val(int,7),())))),
                       ((operation(set_make,(val(int,2),(val(int,4),()))), operation(set_make,(val(int,1),(val(int,2),())))),
                       ()))))).

variable_define(ad,d,operation(multimap_make,
                     ((operation(set_make,(val(int,1),(val(int,2),()))),operation(set_make,(val(int,2),(val(int,4),())))),
                     ((operation(set_make,(val(int,2),(val(int,4),()))),operation(set_make,(val(int,4),(val(int,8),())))),
                     ())))).
variable_define(ae,e,operation(multimap_make,
                     ((operation(set_make,(val(int,1),(val(int,2),()))), operation(set_make,(val(int,2),(val(int,4),())))),
                     ()))).

evaluate(eq,(variable(a),(variable(b),()))).
evaluate(eq,(variable(a),(variable(c),()))).
evaluate(eq,(variable(a),(variable(d),()))).
evaluate(eq,(variable(a),(variable(e),()))).
evaluate(neq,(variable(a),(variable(b),()))).
evaluate(neq,(variable(a),(variable(c),()))).
evaluate(neq,(variable(a),(variable(d),()))).
evaluate(neq,(variable(a),(variable(e),()))).
evaluate(neq,(variable(d),(variable(e),()))).
evaluate(neq,(variable(e),(variable(d),()))).
