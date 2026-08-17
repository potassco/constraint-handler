%%%%%%%%%%%%%%%%% type
_type(bot;int;float;bool;string;symbol;none;set;multimap).

% needed for brave reasoning?
_type_representation((bool;int;string;float;symbol;none),extensional).

_type_representation(set,intensional).
_type_representation(multimap,intensional).

%%%%%%%%%%%%%%%%% eq neq
_type_extensionalEquality(bool).
_type_extensionalEquality(int).
_type_extensionalEquality(string).
_type_extensionalEquality(symbol).

%%%%%%%%%%%%%%%%% leq lt geq gt
_type_extensionalOrder(int).
_type_extensionalOrder(symbol).
_type_extensionalOrder(string).
