%%% capitals = { "germany" : "berlin"; "france" : "paris";  "belarus" : "minsk" }
%%% cities = { "germany" : "berlin", "potsdam", "brest";
%%%            "france" : "paris", "brest";
%%%            "usa" : "paris";
%%%            "belarus" : "brest" }

%%% properDivisors = { 4 : { 1, 2 }; 5 : { 1 }; 6 : { 1, 2, 3 } }
%%% properDivisors2 = { 4 : 1, 2; 5 : 1; 6 : 1, 2, 3 }
%%% sums = { { 1, 2 } :  3;
%%%          { 1 } : 1;
%%%          { 1, 2, 3} : 6 }

%%% nkcaps = #keys capitals = 3
%%% nkpdi1 = #keys properDivisors = 3
%%% nkpdi2 = #keys properDivisors2 = 3
%%% nksums = #keys sums = 3
%%% necaps = #entries capitals = 3
%%% nepdi1 = #entries properDivisors = 3
%%% nepdi2 = #entries properDivisors2 = 6
%%% nesums = #entries sums = 3
%%% siecaps = sum int capitals = 0
%%% siepdi1 = sum int properDivisors = 0
%%% siepdi2 = sum int properDivisors2 = 10
%%% siesums = sum int sums = 10

%%% a = { { 1, 2 } : { 2, 4};
%%%       { 2, 4 } : { 4, 8 }, { 1, 2 }  }
%%% b = { { 1, 2 } : { 1+1, 2+2 };
%%%       b24 : { 1+1, 1 }, b48 }
%%%     where b24 = { 2 * 1, 2 * 2 } and b48 = { 4, 8 }
%%% c = { { 1, 2 } : { 2, 4}; { 2, 4 } : { 4, 7 }, { 1, 2 } }
%%% d = { { 1, 2 } : { 2, 4}; { 2, 4 } : { 4, 8 } }
%%% e = { { 1, 2 } : { 2, 4} }

%%% All:
%%% max cities = "potsdam"     min cities = "brest"
%%% max properDivisors2 = 3     min properDivisors2 = 1
%%% a==b     not a==c     not a==d     not a==e     not a!=b     a!=c     a!=d     a!=e
%%% d!=e     e!=d

%%% f = multimap_fold(myproduct,properDivisors2,100) where myproduct(x,y) = x*y
%%%   =  100 * 1 * 2 * 1 * 1 * 2 * 3 = 1200

%%% l = multimap_fold(snoc,properDivisors2,())) where snoc(tail,head) = (tail, head)
%%%   = (((((((),1),2),1),1),2),3)

variable_define(capitals, operation(multimap_make,
                                ((val(string,"germany"), val(string,"berlin")),
                                ((val(string,"france"), val(string,"paris")),
                                ((val(string,"belarus"), val(string,"minsk")),()))))).

multimap_declare(cities).
multimap_assign(cities,val(string,"germany"),val(string,"berlin")).
multimap_assign(cities,val(string,"germany"),val(string,"potsdam")).
multimap_assign(cities,val(string,"germany"),val(string,"brest")).
multimap_assign(cities,val(string,"france"),val(string,"paris")).
multimap_assign(cities,val(string,"france"),val(string,"brest")).
multimap_assign(cities,val(string,"usa"),val(string,"paris")).
multimap_assign(cities,val(string,"belarus"),val(string,"brest")).

multimap_declare(properDivisors).
multimap_assign(properDivisors,val(int,4),operation(set_make,(val(int,1),(val(int,2), ())))).
multimap_assign(properDivisors,val(int,5),variable(div5)).
variable_define(div5,operation(set_make,(val(int,1),()))).
multimap_assign(properDivisors,val(int,6), variable(div6)).
set_declare(div6).
set_assign(div6,val(int,1)).
set_assign(div6,val(int,2)).
set_assign(div6,val(int,3)).
multimap_assign(properDivisors,val(int,4),variable(div4)).
set_declare(div4).
set_assign(div4,val(int,1)).
set_assign(div4,val(int,2)).

multimap_declare(sums).
multimap_assign(sums,variable(div4),val(int,3)).
multimap_assign(sums,variable(div5),val(int,1)).
multimap_assign(sums,variable(div6),val(int,6)).

multimap_declare(properDivisors2).
multimap_assign(properDivisors2,val(int,4),val(int,1)).
multimap_assign(properDivisors2,val(int,4),val(int,2)).
multimap_assign(properDivisors2,val(int,5),val(int,1)).

multimap_assign(properDivisors2,val(int,6),val(int,1)).
multimap_assign(properDivisors2,val(int,6),val(int,2)).
multimap_assign(properDivisors2,val(int,6),val(int,3)).

evaluate(countKeys,(variable(capitals),())).
evaluate(countKeys,(variable(properDivisors),())).
evaluate(countKeys,(variable(properDivisors2),())).
evaluate(countKeys,(variable(sums),())).

evaluate(countEntries,(variable(capitals),())).
evaluate(countEntries,(variable(properDivisors),())).
evaluate(countEntries,(variable(properDivisors2),())).
evaluate(countEntries,(variable(sums),())).

evaluate(sumIntEntries,(variable(capitals),())).
evaluate(sumIntEntries,(variable(properDivisors),())).
evaluate(sumIntEntries,(variable(properDivisors2),())).
evaluate(sumIntEntries,(variable(sums),())).

evaluate(maxEntries,(variable(cities),())).
evaluate(minEntries,(variable(cities),())).
evaluate(maxEntries,(variable(properDivisors2),())).
evaluate(minEntries,(variable(properDivisors2),())).


evaluate(multimap_fold,(val(function,myproduct),(variable(properDivisors2),(val(int,100),())))).
_computedIdx(E,val(int,VA*VB)) :- _computeIdx(E,myproduct), _computeIdx(E,0,val(int,VA)), _computeIdx(E,1,val(int,VB)).

evaluate(multimap_fold,(val(function,snoc),(variable(properDivisors2),(val(symbol,()),())))).
_computedIdx(E,val(TN,VN)) :- _computeIdx(E,snoc), _computeIdx(E,0,val(TA,VA)), _computeIdx(E,1,val(TB,VB)),
    TN=TB,
    VN=(VB, VA).


multimap_declare(empty).
evaluate(multimap_fold,(val(function,plus),(variable(empty),(val(int,0),())))).
