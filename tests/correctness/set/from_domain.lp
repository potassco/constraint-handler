%%% Test set_declare/1 and set_baseDomain/2
%%%
%%% s contains
%%% * 1 because of set_baseDomain and ensure
%%% * 2 because of set_assign
%%% * maybe 3 because of set_baseDomain
%%% * 4 because of set_assign

variable_declare(s,set).
set_baseDomain(s,val(int,1..3)).
ensure(operation(set_isin,(val(int,1),(variable(s),())))).
set_assign(s,val(int,(2;4))).


set_declare(s2).
set_baseDomain(s2,val(int,1..3)).
ensure(operation(set_isin,(val(int,1),(variable(s2),())))).
set_assign(s2,val(int,(2;4))).
