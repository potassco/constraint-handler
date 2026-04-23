%%% m1 = { "a" : 1, "b" : 2,3 }
%%% m2 = declare multimap
%%% assign m2 "a" 4
%%% assign m2 "b" 5
%%% assign m2 "b" 6
%%% m3 = { "a" : 4, "b" : 5,3+3 }
%%% in5 = { 5 : "c", "c" : 6 }[5] = { "c" }
%%% inc = { 5 : "c", "c" : 6 }["c"] = { 6 }
%%% in6 = { 5 : "c", "c" : 6 }[6] = {}
%%% multimap_isin5 = 5 multimap_isin { 5 : "c", "c" : 6 } = true
%%% multimap_isin6 = 6 multimap_isin { 5 : "c", "c" : 6 } = false
%%% m1a = m1["a"]  m1b = m1["b"]  m1c = m1["c"]
%%% m2a = m2["a"]  m2b = m2["b"]  m2c = m2["c"]

%%% all:
%%% m1a == { 1 }    m1b == { 2,3 }    m1c == {}
%%% m2a == { 4 }    m2b == { 5,6 }    m2c == {}
%%% in5 == { "c" }  inc == { 6 }    in6 == {}
%%% "a" multimap_isin m1     "c" multimap_isin m1 == false     1 multimap_isin m1 == false
%%% "a" multimap_isin m2     "c" multimap_isin m2 == false     4 multimap_isin m2 == false
%%% multimap_isin5           multimap_isin6 == false
%%% multimap_value(m1,"a",1)
%%% multimap_value(m1,"b",2)
%%% multimap_value(m1,"b",3)
%%% multimap_value(m2,"a",4)
%%% multimap_value(m2,"b",5)
%%% multimap_value(m2,"b",6)
%%% m1 != m2
%%% m2 == m3
%%% m1 != m1

variable_define(m1, operation(multimap_make,
                           ((val(string,"a"), val(int,1)),
                           ((val(string,"b"), val(int,2)),
                           ((val(string,"b"), val(int,3)),()))))).

multimap_declare(m2).
multimap_assign(m2,val(string,"a"),val(int,4)).
multimap_assign(m2,val(string,"b"),val(int,5)).
multimap_assign(m2,val(string,"b"),val(int,6)).

variable_define(m3, operation(multimap_make,
                           ((val(string,"a"), val(int,4)),
                           ((val(string,"b"), val(int,5)),
                           ((val(string,"b"), operation(add,(val(int,3),(val(int,3),())))),()))))).

variable_define(in5,EXPR) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(string,"c")),
                           ((val(string,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(int,5),(MAP,()))).
variable_define(inc,EXPR) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(string,"c")),
                           ((val(string,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(string,"c"),(MAP,()))).
variable_define(in6,EXPR) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(string,"c")),
                           ((val(string,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(int,6),(MAP,()))).

variable_define(m1a,operation(find,(val(string,"a"),(variable(m1),())))).
variable_define(m1b,operation(find,(val(string,"b"),(variable(m1),())))).
variable_define(m1c,operation(find,(val(string,"c"),(variable(m1),())))).
variable_define(m2a,operation(find,(val(string,"a"),(variable(m2),())))).
variable_define(m2b,operation(find,(val(string,"b"),(variable(m2),())))).
variable_define(m2c,operation(find,(val(string,"c"),(variable(m2),())))).

evaluate(eq,(variable(m1a),(operation(set_make,(val(int,1),())),()))).
evaluate(eq,(variable(m1b),(operation(set_make,(val(int,2),(val(int,3),()))),()))).
evaluate(eq,(variable(m1c),(operation(set_make,(())),()))).
evaluate(eq,(variable(m2a),(operation(set_make,(val(int,4),())),()))).
evaluate(eq,(variable(m2b),(operation(set_make,(val(int,5),(val(int,6),()))),()))).
evaluate(eq,(variable(m2c),(operation(set_make,()),()))).
evaluate(eq,(variable(in5),(operation(set_make,(val(string,"c"),())),()))).
evaluate(eq,(variable(inc),(operation(set_make,(val(int,6),())),()))).
evaluate(eq,(variable(in6),(operation(set_make,()),()))).

evaluate(multimap_isin,(val(string,"a"),(variable(m1),()))).
evaluate(multimap_isin,(val(string,"c"),(variable(m1),()))).
evaluate(multimap_isin,(val(int,1),(variable(m1),()))).
evaluate(multimap_isin,(val(string,"a"),(variable(m2),()))).
evaluate(multimap_isin,(val(string,"c"),(variable(m2),()))).
evaluate(multimap_isin,(val(int,4),(variable(m2),()))).

variable_define(multimap_isin5,operation(multimap_isin,(val(int,5),(MAP,())))) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(string,"c")),
                           ((val(string,"c"), val(int,6)),()))).
variable_define(multimap_isin6,operation(multimap_isin,(val(int,6),(MAP,())))) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(string,"c")),
                           ((val(string,"c"), val(int,6)),()))).

evaluate(neq,(variable(m1),(variable(m2),()))).
evaluate(eq,(variable(m2),(variable(m3),()))).
evaluate(eq,(variable(m3),(variable(m1),()))).
