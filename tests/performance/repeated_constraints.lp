% Compile benchmark: many identical singleton constraints generated via
% first-order variables so the encoding shape is repeated many times.

#const pair_count = 1000.

pair(1..pair_count).

variable_declare(left(I),fromFacts,d_left(I)) :- pair(I).
variable_domain(left(I),val(int,I)) :- pair(I).

variable_declare(right(I),fromFacts,d_right(I)) :- pair(I).
variable_domain(right(I),val(int,I+1)) :- pair(I).

ensure(
    operation(
        eq,
        (
            operation(add,(variable(left(I)),(val(int,1),()))),
            (variable(right(I)),())
        )
    )
,match(I)) :- pair(I).
