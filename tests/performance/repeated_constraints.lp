% Compile benchmark: many identical singleton constraints generated via
% first-order variables so the encoding shape is repeated many times.

#const pair_count = 1000.

pair(1..pair_count).

variable_declare(d_left(I),left(I),fromFacts) :- pair(I).
variable_domain(left(I),val(int,I)) :- pair(I).

variable_declare(d_right(I),right(I),fromFacts) :- pair(I).
variable_domain(right(I),val(int,I+1)) :- pair(I).

ensure(
    match(I),
    operation(
        eq,
        (
            operation(add,(variable(left(I)),(val(int,1),()))),
            (variable(right(I)),())
        )
    )
) :- pair(I).
