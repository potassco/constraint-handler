
_operator_declared(O) :- operator_declare(O,_,_).
_operator_declared(O) :- operator_declare_variadic(O,_,_,_).
_operator_safe(O) :- _operator_declared(O), not _operator_unsafe(O).

% bool
operator_declare((eq;neq),(T1,(T2,())),bool) :- _type(T1), _type(T2), (T1;T2)=none.
operator_declare_variadic((lxor;leqv),bool,bool,1).
operator_declare((lnot;snot;wnot),(bool,()),bool).
operator_declare(lnot,(none,()),none).
operator_declare((snot;wnot),(bool,()),none).
operator_declare_variadic((conj;disj),bool,bool,1).
_operator_recoverable((conj;disj)).
_operator_recoverable(limp).

% conditionals
operator_declare(ite,(bool,(T,(T,()))),T) :- _type(T).
_operator_recoverable(ite).
_operator_recoverable(if).
_operator_recoverable(default).
operator_declare(hasValue,(T,()),bool) :- _type(T).

% equality
operator_declare((eq;neq),(T,(T,())),bool) :- _type_extensionalEquality(T).
operator_declare((leq;lt;geq;gt),(T,(T,())),bool) :- _type_extensionalOrder(T).

% float
intToFloatOperator(sqrt;cos;sin;tan;acos;asin;atan).
floatUnOperator(abs;sqrt;cos;sin;tan;acos;asin;atan;minus;ceil;floor).
floatFloatFloatOperator(add;sub;mult;float_div;pow;max;min).
floatBinOperator(OP) :- floatFloatFloatOperator(OP).
floatBinOperator(int_div;leq;lt;geq;gt).


operator_declare_variadic((add;mult),float,float,2).
operator_declare(OP,((int;float),()),float) :- intToFloatOperator(OP).
operator_declare((abs;minus),(float,()),float).
operator_declare(ceil,(float,()),int).
operator_declare(floor,(float,()),int).
operator_declare(OP,(T1,(T2,())),float) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int), floatFloatFloatOperator(OP).
operator_declare(float_div,(int,(int,())),float).
operator_declare((leq;lt;geq;gt),(T1,(T2,())),bool) :- T1 = (int;float),T2 = (int;float), (T1,T2) != (int,int).
operator_declare((eq;neq),(float,(float,())),bool).

% int
operator_declare_variadic((add;mult),int,int,1).
operator_declare((sub;pow),(int,(int,())),int).
_operator_recoverable(pow).
operator_declare(int_div,((int;float),((int;float),())),int).
operator_declare((abs;ceil;floor;minus),(int,()),int).

% multimap
operator_declare_variadic(multimap_make,(K,V),multimap,1) :- _type(K), _type(V).
operator_declare(find,(T1,(multimap,())),set) :- _type(T1).
operator_declare((countKeys;countEntries;sumIntEntries),(multimap,()),int).
operator_declare((eq;neq),(multimap,(multimap,())),bool).
operator_declare(multimap_isin,(T1,(multimap,())),bool) :- _type(T1).

% set
operator_declare(length,(set,()),int).
operator_declare((set_isin;set_notin),(T1,(set,())),bool) :- _type(T1).
operator_declare_variadic(set_make,T,set,1) :- _type(T).
operator_declare((union;inter;diff),(set,(set,())),set).
operator_declare((eq;neq),(set,(set,())),bool).
operator_declare(subset,(set,(set,())),bool).

% string
operator_declare(length,(string,()),int).
operator_declare(concat,(string,(string,())),string).
