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

variable_define(acap, capitals, operation(multimap_make,
                                ((val(str,"germany"), val(str,"berlin")),
                                ((val(str,"france"), val(str,"paris")),
                                ((val(str,"belarus"), val(str,"minsk")),()))))).

multimap_declare(dc,cities).
multimap_assign(ac,cities,val(str,"germany"),val(str,"berlin")).
multimap_assign(ac,cities,val(str,"germany"),val(str,"potsdam")).
multimap_assign(ac,cities,val(str,"germany"),val(str,"brest")).
multimap_assign(ac,cities,val(str,"france"),val(str,"paris")).
multimap_assign(ac,cities,val(str,"france"),val(str,"brest")).
multimap_assign(ac,cities,val(str,"usa"),val(str,"paris")).
multimap_assign(ac,cities,val(str,"belarus"),val(str,"brest")).

multimap_declare(dpd,properDivisors).
multimap_assign(apd,properDivisors,val(int,4),operation(set_make,(val(int,1),(val(int,2), ())))).
multimap_assign(apd,properDivisors,val(int,5),variable(div5)).
variable_define(apd,div5,operation(set_make,(val(int,1),()))).
multimap_assign(apd,properDivisors,val(int,6), variable(div6)).
set_declare(dpd,div6).
set_assign(apd,div6,val(int,1)).
set_assign(apd,div6,val(int,2)).
set_assign(apd,div6,val(int,3)).
multimap_assign(apd,properDivisors,val(int,4),variable(div4)).
set_declare(dpd,div4).
set_assign(apd,div4,val(int,1)).
set_assign(apd,div4,val(int,2)).

multimap_declare(ds,sums).
multimap_assign(as,sums,variable(div4),val(int,3)).
multimap_assign(as,sums,variable(div5),val(int,1)).
multimap_assign(as,sums,variable(div6),val(int,6)).

multimap_declare(dpd2,properDivisors2).
multimap_assign(apd2,properDivisors2,val(int,4),val(int,1)).
multimap_assign(apd2,properDivisors2,val(int,4),val(int,2)).
multimap_assign(apd2,properDivisors2,val(int,5),val(int,1)).

multimap_assign(apd2,properDivisors2,val(int,6),val(int,1)).
multimap_assign(apd2,properDivisors2,val(int,6),val(int,2)).
multimap_assign(apd2,properDivisors2,val(int,6),val(int,3)).

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


multimap_declare(m_empty,empty).
evaluate(multimap_fold,(val(function,plus),(variable(empty),(val(int,0),())))).
