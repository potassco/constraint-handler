#include "includeAll.lp".

%%% capitals = { "germany" : "berlin"; "france" : "paris";  "belarus" : "minsk" }
%%% cities = { "germany" : "berlin", "potsdam", "brest";
%%%            "france" : "paris", "brest";
%%%            "usa" : "paris";
%%%            "belarus" : "brest" }

%%% properDivisors = { 4 : { 1, 2 }, 5 : { 1 }, 6 : { 1, 2, 3} }
%%% properDivisors2 = { 4 : 1, 2; 5 : 1; 6 : 1, 2, 3 }
%%% sums = { { 1, 2 } :  3;
%%%          { 1 } : 1;
%%%          { 1, 2, 3} : 6 }

%%% nkcaps = #keys capitals
%%% nkpdi1 = #keys properDivisors
%%% nkpdi2 = #keys properDivisors
%%% nksums = #keys sums
%%% necaps = #entries capitals
%%% nepdi1 = #entries properDivisors
%%% nepdi2 = #entries properDivisors2
%%% nesums = #entries sums
%%% siecaps = sum int capitals
%%% siepdi1 = sum int properDivisors
%%% siepdi2 = sum int properDivisors2
%%% siesums = sum int sums

%#show multimap_value/5.
%#show eValue/3.
%#show expression/1.
%#show multimapHas/4.
%#show multimap_entry/5.
%#show multimap_assign/4.
%#show compileAssignToMultimap/4.
%#show representative/5.
%#show testEqual/3.
%#show testedEqual/3.

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
assignToSet(apd, div6,constant(int(1))).
assignToSet(apd, div6,constant(int(2))).
assignToSet(apd, div6,constant(int(3))).
multimap_assign(apd, properDivisors, constant(int(4)), variable(div4)).
assignToSet(apd, div4,constant(int(1))).
assignToSet(apd, div4,constant(int(2))).

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
