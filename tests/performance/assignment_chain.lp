% Compile benchmark: deep execution snippet made of many simple assignments.

#const chain_length = 200.

max_step(chain_length).
step(1..K) :- max_step(K).

stmt(1, assign(t(1), val(int, 1))).
stmt(K + 1, seq2(S, assign(t(K + 1), operation(add, (variable(t(K)), (val(int, 1), ())))))) :-
    stmt(K, S),
    step(K),
    max_step(M),
    K < M.

execution_declare(counter, S, (), (t(M), ())) :-
    stmt(M, S),
    max_step(M).

execution_run(counter).
