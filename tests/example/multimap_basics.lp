%%% m1 = { "a" : 1, "b" : 2,3 }
%%% m2 = declare multimap
%%% assign m2 "a" 4
%%% assign m2 "b" 5
%%% assign m2 "b" 6
%%% m3 = { "a" : 4, "b" : 5,3+3 }
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
%%% m1 != m2
%%% m2 == m3
%%% m1 != m1

variable_define(dummy, m1, operation(multimap_make,
                           ((val(str,"a"), val(int,1)),
                           ((val(str,"b"), val(int,2)),
                           ((val(str,"b"), val(int,3)),()))))).

multimap_declare(dummy,m2).
multimap_assign(dummy,m2,val(str,"a"),val(int,4)).
multimap_assign(dummy,m2,val(str,"b"),val(int,5)).
multimap_assign(dummy,m2,val(str,"b"),val(int,6)).

variable_define(dummy, m3, operation(multimap_make,
                           ((val(str,"a"), val(int,4)),
                           ((val(str,"b"), val(int,5)),
                           ((val(str,"b"), operation(add,(val(int,3),(val(int,3),())))),()))))).

variable_define(dummy,in5,EXPR) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(int,5),(MAP,()))).
variable_define(dummy,inc,EXPR) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(str,"c"),(MAP,()))).
variable_define(dummy,in6,EXPR) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))),
  EXPR = operation(find,(val(int,6),(MAP,()))).

variable_define(dummy,m1a,operation(find,(val(str,"a"),(variable(m1),())))).
variable_define(dummy,m1b,operation(find,(val(str,"b"),(variable(m1),())))).
variable_define(dummy,m1c,operation(find,(val(str,"c"),(variable(m1),())))).
variable_define(dummy,m2a,operation(find,(val(str,"a"),(variable(m2),())))).
variable_define(dummy,m2b,operation(find,(val(str,"b"),(variable(m2),())))).
variable_define(dummy,m2c,operation(find,(val(str,"c"),(variable(m2),())))).

evaluate(eq,(variable(m1a),(operation(set_make,(val(int,1),())),()))).
evaluate(eq,(variable(m1b),(operation(set_make,(val(int,2),(val(int,3),()))),()))).
evaluate(eq,(variable(m1c),(operation(set_make,(())),()))).
evaluate(eq,(variable(m2a),(operation(set_make,(val(int,4),())),()))).
evaluate(eq,(variable(m2b),(operation(set_make,(val(int,5),(val(int,6),()))),()))).
evaluate(eq,(variable(m2c),(operation(set_make,()),()))).
evaluate(eq,(variable(in5),(operation(set_make,(val(str,"c"),())),()))).
evaluate(eq,(variable(inc),(operation(set_make,(val(int,6),())),()))).
evaluate(eq,(variable(in6),(operation(set_make,()),()))).

evaluate(isin,(val(str,"a"),(variable(m1),()))).
evaluate(isin,(val(str,"c"),(variable(m1),()))).
evaluate(isin,(val(int,1),(variable(m1),()))).
evaluate(isin,(val(str,"a"),(variable(m2),()))).
evaluate(isin,(val(str,"c"),(variable(m2),()))).
evaluate(isin,(val(int,4),(variable(m2),()))).

variable_define(dummy,isin5,operation(isin,(val(int,5),(MAP,())))) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))).
variable_define(dummy,isin6,operation(isin,(val(int,6),(MAP,())))) :-
  MAP = operation(multimap_make,
                           ((val(int,5), val(str,"c")),
                           ((val(str,"c"), val(int,6)),()))).

evaluate(neq,(variable(m1),(variable(m2),()))).
evaluate(eq,(variable(m2),(variable(m3),()))).
evaluate(eq,(variable(m3),(variable(m1),()))).
