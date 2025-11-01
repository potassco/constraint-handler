#include "includeAll.lp".

%%% m1 = { "a" : 1, "b" : 2 }
%%% m2 = declare multimap
%%% m2["a"] = 3
%%% m2["b"] = 4
%%% in5 = { 5 : "c", "c" : 6 }[5]
%%% inc = { 5 : "c", "c" : 6 }["c"]
%%% in6 = { 5 : "c", "c" : 6 }[6]
%%% isin5 = 5 isin { 5 : "c", "c" : 6 }
%%% isin6 = 6 isin { 5 : "c", "c" : 6 }

%%% all:
%%% m1["a"] == 1    m1["b"] == 2    default(m1["c"],true) == true
%%% m2["a"] == 3    m2["b"] == 4    default(m2["c"],17) == 17
%%% in5 == "c"      inc == 6        default(in6,false) == false
%%% "a" isin m1     "c" isin m1 == false     1 isin m1 == false
%%% "a" isin m2     "c" isin m2 == false     3 isin m2 == false
%%% isin5           isin6 == false
assign(dummy, m1, operation(multimapMake,
                           ((val(str,"a"), val(int,1)),
                           ((val(str,"b"), val(int,2)),())))).

multimap_declare(dummy,m2).
multimap_assign(dummy,m2,val(str,"a"),val(int,3)).
multimap_assign(dummy,m2,val(str,"b"),val(int,4)).

assign(dummy,in5,EXPR) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(int,5),(MAP,()))).
assign(dummy,inc,EXPR) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(str,"c"),(MAP,()))).
assign(dummy,in6,EXPR) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(int,6),(MAP,()))).

evaluate(find,(val(str,"a"),(variable(m1),()))).
evaluate(find,(val(str,"b"),(variable(m1),()))).
evaluate(default,(operation(find,(val(str,"c"),(variable(m1),()))),(val(bool,true),()))).
evaluate(find,(val(str,"a"),(variable(m2),()))).
evaluate(find,(val(str,"b"),(variable(m2),()))).
evaluate(default,(operation(find,(val(str,"c"),(variable(m2),()))),(val(int,17),()))).
evaluate(eq,(variable(in5),(val(str,"c"),()))).
evaluate(eq,(variable(inc),(val(int,6),()))).
evaluate(default,(variable(in6),(val(bool,false),()))).

evaluate(isin,(val(str,"a"),(variable(m1),()))).
evaluate(isin,(val(str,"c"),(variable(m1),()))).
evaluate(isin,(val(int,1),(variable(m1),()))).
evaluate(isin,(val(str,"a"),(variable(m2),()))).
evaluate(isin,(val(str,"c"),(variable(m2),()))).
evaluate(isin,(val(int,3),(variable(m2),()))).

assign(dummy,isin5,operation(isin,(val(int,5),(MAP,())))) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))).
assign(dummy,isin6,operation(isin,(val(int,6),(MAP,())))) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))).
