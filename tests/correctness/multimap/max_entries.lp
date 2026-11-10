%%% cities = { "germany" : "berlin", "potsdam", "brest";
%%%            "france" : "paris", "brest";
%%%            "usa" : "paris";
%%%            "belarus" : "brest" }
%%% properDivisors2 = { 4 : 1, 2; 5 : 1; 6 : 1, 2, 3 }
%%% max cities = "potsdam"
%%% max properDivisors2 = 3

variable_declare(cities,multimap).
multimap_assign(cities,val(string,"germany"),val(string,"berlin")).
multimap_assign(cities,val(string,"germany"),val(string,"potsdam")).
multimap_assign(cities,val(string,"germany"),val(string,"brest")).
multimap_assign(cities,val(string,"france"),val(string,"paris")).
multimap_assign(cities,val(string,"france"),val(string,"brest")).
multimap_assign(cities,val(string,"usa"),val(string,"paris")).
multimap_assign(cities,val(string,"belarus"),val(string,"brest")).

variable_declare(properDivisors2,multimap).
multimap_assign(properDivisors2,val(int,4),val(int,1)).
multimap_assign(properDivisors2,val(int,4),val(int,2)).
multimap_assign(properDivisors2,val(int,5),val(int,1)).
multimap_assign(properDivisors2,val(int,6),val(int,1)).
multimap_assign(properDivisors2,val(int,6),val(int,2)).
multimap_assign(properDivisors2,val(int,6),val(int,3)).

evaluate(operation(multimap_maxEntries,(variable(cities),()))).
evaluate(operation(multimap_maxEntries,(variable(properDivisors2),()))).
