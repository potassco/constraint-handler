#include "includeAll.lp".

%%% m1 = { "a" : 1, "b" : 2,3 }
%%% m2 = declare multimap
%%% assign m2 "a" 4
%%% assign m2 "b" 5
%%% assign m2 "b" 6
%%% in5 = { 5 : "c", "c" : 6 }[5] = { "c" }
%%% inc = { 5 : "c", "c" : 6 }["c"] = { 6 }
%%% in6 = { 5 : "c", "c" : 6 }[6] = {}
%%% isin5 = 5 isin { 5 : "c", "c" : 6 } = true
%%% isin6 = 6 isin { 5 : "c", "c" : 6 } = false
%%% m1a = m1["a"]  m1b = m1["b"]  m1c = m1["c"]
%%% m2a = m2["a"]  m2b = m2["b"]  m2c = m2["c"]

%%% all:
%%% m1a == { 1 }    m1b == { 2,3 }    m1c == {}
%%% m2a == { 4 }    m2b == { 5,6 }    m2c == {}
%%% in5 == { "c" }  inc == { 6 }    in6 == {}
%%% "a" isin m1     "c" isin m1 == false     1 isin m1 == false
%%% "a" isin m2     "c" isin m2 == false     4 isin m2 == false
%%% isin5           isin6 == false
%%% multimap_value(m1,"a",1)
%%% multimap_value(m1,"b",2)
%%% multimap_value(m1,"b",3)
%%% multimap_value(m2,"a",4)
%%% multimap_value(m2,"b",5)
%%% multimap_value(m2,"b",6)

assign(dummy, m1, operation(multimapMake,
                           ((val(str,"a"), val(int,1)),
                           ((val(str,"b"), val(int,2)),
                           ((val(str,"b"), val(int,3)),()))))).

multimap_declare(dummy,m2).
multimap_assign(dummy,m2,val(str,"a"),val(int,4)).
multimap_assign(dummy,m2,val(str,"b"),val(int,5)).
multimap_assign(dummy,m2,val(str,"b"),val(int,6)).

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

variable_define(dummy,m1a,operation(find,(val(str,"a"),(variable(m1),())))).
variable_define(dummy,m1b,operation(find,(val(str,"b"),(variable(m1),())))).
variable_define(dummy,m1c,operation(find,(val(str,"c"),(variable(m1),())))).
variable_define(dummy,m2a,operation(find,(val(str,"a"),(variable(m2),())))).
variable_define(dummy,m2b,operation(find,(val(str,"b"),(variable(m2),())))).
variable_define(dummy,m2c,operation(find,(val(str,"c"),(variable(m2),())))).
#show evaluated/4.
evaluate(eq,(variable(m1a),(operation(makeSet,(val(int,1),())),()))).
evaluate(eq,(variable(m1b),(operation(makeSet,(val(int,2),(val(int,3),()))),()))).
evaluate(eq,(variable(m1c),(operation(makeSet,(())),()))).
evaluate(eq,(variable(m2a),(operation(makeSet,(val(int,4),())),()))).
evaluate(eq,(variable(m2b),(operation(makeSet,(val(int,5),(val(int,6),()))),()))).
evaluate(eq,(variable(m2c),(operation(makeSet,()),()))).
evaluate(eq,(variable(in5),(operation(makeSet,(val(str,"c"),())),()))).
evaluate(eq,(variable(inc),(operation(makeSet,(val(int,6),())),()))).
evaluate(eq,(variable(in6),(operation(makeSet,()),()))).

evaluate(isin,(val(str,"a"),(variable(m1),()))).
evaluate(isin,(val(str,"c"),(variable(m1),()))).
evaluate(isin,(val(int,1),(variable(m1),()))).
evaluate(isin,(val(str,"a"),(variable(m2),()))).
evaluate(isin,(val(str,"c"),(variable(m2),()))).
evaluate(isin,(val(int,4),(variable(m2),()))).

assign(dummy,isin5,operation(isin,(val(int,5),(MAP,())))) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))).
assign(dummy,isin6,operation(isin,(val(int,6),(MAP,())))) :-
  MAP = operation(multimapMake,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))).
