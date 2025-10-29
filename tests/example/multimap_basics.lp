#include "includeAll.lp".

%%% m1 = { "a" : 1, "b" : 2 }
%%% m2 = declare multimap
%%% m2["a"] = 3
%%% m2["b"] = 4
%%% in5 = { 5 : "c", "c" : 6 }[5]
%%% inc = { 5 : "c", "c" : 6 }["c"]
%%% in6 = { 5 : "c", "c" : 6 }[6]

%%% all:
%%% m1["a"] == 1    m1["b"] == 2    default(m1["c"],true) == true
%%% m2["a"] == 3    m2["b"] == 4    default(m2["c"],17) == 17
%%% in5 == "c"    inc == 6    default(in6,false) == false

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
