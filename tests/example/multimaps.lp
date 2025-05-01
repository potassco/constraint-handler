#include "includeAll.lp".

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
%%% maxcities = max cities = "potsdam"
%%% mincities = min cities = "brest"
%%% maxpdi2 = max properDivisors2 = 3
%%% minpdi2 = min properDivisors2 = 1

%%% a = { { 1, 2 } : { 2, 4};
%%%       { 2, 4 } : { 4, 8 }, { 1, 2 }  }
%%% b = { { 1, 2 } : { 1+1, 2+2 };
%%%       b24 : { 1+1, 1 }, b48 }
%%%     where b24 = { 2 * 1, 2 * 2 } and b48 = { 4, 8 }
%%% c = { { 1, 2 } : { 2, 4}; { 2, 4 } : { 4, 7 }, { 1, 2 } }
%%% d = { { 1, 2 } : { 2, 4}; { 2, 4 } : { 4, 8 } }
%%% e = { { 1, 2 } : { 2, 4} }
%%% eab = a == b = true
%%% eac = a == c = false
%%% ead = a == d = false
%%% eae = a == e = false
%%% nab = a != b = false
%%% nac = a != c = true
%%% nad = a != d = true
%%% nad = a != e = true

%%% f = fold(myproduct,properDivisors2,100) where myproduct(x,y) = x*y
%%%   =  100 * 1 * 2 * 1 * 1 * 2 * 3 = 1200

%%% l = fold(snoc,properDivisors2,())) where snoc(tail,head) = (tail, head)
%%%   = (((((((),1),2),1),1),2),3)

assign(acap, capitals, operation(multimapMake,
                                (constant(str("germany")), (constant(str("berlin")),
                                (constant(str("france")), (constant(str("paris")),
                                (constant(str("belarus")), (constant(str("minsk")),())))))))).

multimap_declare(dc,cities).
multimap_assign(ac, cities, constant(str("germany")), constant(str("berlin"))).
multimap_assign(ac, cities, constant(str("germany")), constant(str("potsdam"))).
multimap_assign(ac, cities, constant(str("germany")), constant(str("brest"))).
multimap_assign(ac, cities, constant(str("france")), constant(str("paris"))).
multimap_assign(ac, cities, constant(str("france")), constant(str("brest"))).
multimap_assign(ac, cities, constant(str("usa")), constant(str("paris"))).
multimap_assign(ac, cities, constant(str("belarus")), constant(str("brest"))).

multimap_declare(dpd,properDivisors).
multimap_assign(apd, properDivisors, constant(int(4)), operation(makeSet,(constant(int(1)), (constant(int(2)), ())))).
multimap_assign(apd, properDivisors, constant(int(5)), variable(div5)).
assign(apd, div5,operation(makeSet,(constant(int(1)), ()))).
multimap_assign(apd, properDivisors, constant(int(6)), variable(div6)).
set_declare(dpd, div6).
set_assign(apd, div6,constant(int(1))).
set_assign(apd, div6,constant(int(2))).
set_assign(apd, div6,constant(int(3))).
multimap_assign(apd, properDivisors, constant(int(4)), variable(div4)).
set_declare(dpd, div4).
set_assign(apd, div4,constant(int(1))).
set_assign(apd, div4,constant(int(2))).

multimap_declare(ds,sums).
multimap_assign(as, sums, variable(div4), constant(int(3))).
multimap_assign(as, sums, variable(div5), constant(int(1))).
multimap_assign(as, sums, variable(div6), constant(int(6))).

multimap_declare(dpd2,properDivisors2).
multimap_assign(apd2, properDivisors2, constant(int(4)), constant(int(1))).
multimap_assign(apd2, properDivisors2, constant(int(4)), constant(int(2))).
multimap_assign(apd2, properDivisors2, constant(int(5)), constant(int(1))).

multimap_assign(apd2, properDivisors2, constant(int(6)), constant(int(1))).
multimap_assign(apd2, properDivisors2, constant(int(6)), constant(int(2))).
multimap_assign(apd2, properDivisors2, constant(int(6)), constant(int(3))).

assign(ankcaps, nkcaps, operation(countKeys,(variable(capitals),()))).
assign(ankpdi1, nkpdi1, operation(countKeys,(variable(properDivisors),()))).
assign(ankpdi2, nkpdi2, operation(countKeys,(variable(properDivisors2),()))).
assign(anksums, nksums, operation(countKeys,(variable(sums),()))).

assign(ankcaps, necaps, operation(countEntries,(variable(capitals),()))).
assign(ankpdi1, nepdi1, operation(countEntries,(variable(properDivisors),()))).
assign(ankpdi2, nepdi2, operation(countEntries,(variable(properDivisors2),()))).
assign(anksums, nesums, operation(countEntries,(variable(sums),()))).

assign(ankcaps, siecaps, operation(sumIntEntries,(variable(capitals),()))).
assign(ankpdi1, siepdi1, operation(sumIntEntries,(variable(properDivisors),()))).
assign(ankpdi2, siepdi2, operation(sumIntEntries,(variable(properDivisors2),()))).
assign(anksums, siesums, operation(sumIntEntries,(variable(sums),()))).

assign(maxmin, maxcities, operation(maxEntries,(variable(cities),()))).
assign(maxmin, mincities, operation(minEntries,(variable(cities),()))).
assign(maxmin, maxpdi2, operation(maxEntries,(variable(properDivisors2),()))).
assign(maxmin, minpdi2, operation(minEntries,(variable(properDivisors2),()))).

assign(aa, a, operation(multimapMake,
                       (operation(makeSet,(constant(int(1)),(constant(int(2)),()))), (operation(makeSet,(constant(int(2)),(constant(int(4)),()))),
                       (operation(makeSet,(constant(int(2)),(constant(int(4)),()))), (operation(makeSet,(constant(int(4)),(constant(int(8)),()))),
                       (operation(makeSet,(constant(int(2)),(constant(int(4)),()))), (operation(makeSet,(constant(int(1)),(constant(int(2)),()))),
                       ())))))))).

multimap_declare(ab,b).
multimap_assign(ab,b,
    operation(makeSet,(constant(int(1)),(constant(int(2)),()))),
    operation(makeSet,
             (operation(add,(constant(int(1)),(constant(int(1)),()))),
             (operation(add,(constant(int(2)),(constant(int(2)),()))),())))).

assign(abs,b24,
    operation(makeSet,
        (operation(mult,(constant(int(2)),(constant(int(1)),()))),
        (operation(mult,(constant(int(2)),(constant(int(2)),()))),())))).
multimap_assign(ab,b,
    variable(b24),
    operation(makeSet,
             (operation(add,(constant(int(1)),(constant(int(1)),()))),
             (constant(int(1)),
             ())))).

set_declare(dbs, b48).
set_assign(abs, b48, constant(int(4))).
set_assign(abs, b48, constant(int(8))).

multimap_assign(ab,b,
    variable(b24),
    variable(b48)).

assign(ac, c, operation(multimapMake,
                       (operation(makeSet,(constant(int(1)),(constant(int(2)),()))), (operation(makeSet,(constant(int(2)),(constant(int(4)),()))),
                       (operation(makeSet,(constant(int(2)),(constant(int(4)),()))), (operation(makeSet,(constant(int(4)),(constant(int(7)),()))),
                       (operation(makeSet,(constant(int(2)),(constant(int(4)),()))), (operation(makeSet,(constant(int(1)),(constant(int(2)),()))),
                       ())))))))).

assign(ad, d, operation(multimapMake,
                       (operation(makeSet,(constant(int(1)),(constant(int(2)),()))), (operation(makeSet,(constant(int(2)),(constant(int(4)),()))),
                       (operation(makeSet,(constant(int(2)),(constant(int(4)),()))), (operation(makeSet,(constant(int(4)),(constant(int(8)),()))),
                       ())))))).
assign(ae, e, operation(multimapMake,
                       (operation(makeSet,(constant(int(1)),(constant(int(2)),()))), (operation(makeSet,(constant(int(2)),(constant(int(4)),()))),
                       ())))).

assign(aeab, eab, operation(eq, (variable(a),(variable(b),())))).
assign(aeac, eac, operation(eq, (variable(a),(variable(c),())))).
assign(aead, ead, operation(eq, (variable(a),(variable(d),())))).
assign(aeae, eae, operation(eq, (variable(a),(variable(e),())))).
assign(anab, nab, operation(neq,(variable(a),(variable(b),())))).
assign(anac, nac, operation(neq,(variable(a),(variable(c),())))).
assign(anad, nad, operation(neq,(variable(a),(variable(d),())))).
assign(anae, nae, operation(neq,(variable(a),(variable(e),())))).

assign(afold, f, operation(fold,(constant(symbol(myproduct)),(variable(properDivisors2),(constant(int(100)),()))))).

computed(myproduct,ARGS,int,VA * VB) :- compute(myproduct,ARGS),
    ARGS = (int,(VA,(int,(VB,())))).

assign(afoldl, l, operation(fold,(constant(symbol(snoc)),(variable(properDivisors2),(constant(symbol(())),()))))).
computed(snoc,ARGS,TN,VN) :- compute(snoc,ARGS),
    ARGS = (TA,(VA,(TB,(VB,())))),
    TN = TB, VN = (VB, VA).
