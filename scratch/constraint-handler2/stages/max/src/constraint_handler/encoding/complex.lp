complex_solution(Id, SolutionId) :-
    %engine(complex, Id) % makes grounding slow
    solution(Id, SolutionId),
    value(Arg, Input) : input(SolutionId, Arg, Input);
    tuple_size(Arg, Size) : input_tuple_size(SolutionId, Arg, Size);
    set_value(Arg, IncludedValue) : set_input_include(SolutionId, Arg, IncludedValue);
    not set_value(Arg, ExcludedValue) : set_input_exclude(SolutionId, Arg, ExcludedValue).

value(Id, V) :- complex_solution(Id, SolutionId), output(SolutionId, Out), value(Out, V).
set_value(Id, M) :- complex_solution(Id, SolutionId), output(SolutionId, Out), set_value(Out, M).
tuple_size(Id, N) :- complex_solution(Id, SolutionId), output(SolutionId, Out), tuple_size(Out, N).
value(__tuple(Id, I), V) :- complex_solution(Id, SolutionId), output(SolutionId, Out),
    tuple_size(Out, N), I = 0..N-1, value(__tuple(Out, I), V).
set_value(__tuple(Id, I), M) :- complex_solution(Id, SolutionId), output(SolutionId, Out),
    tuple_size(Out, N), I = 0..N-1, set_value(__tuple(Out, I), M).