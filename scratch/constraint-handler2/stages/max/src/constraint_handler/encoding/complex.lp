complex_solution(Id, SolutionId) :-
    %engine(complex, Id) % makes grounding slow
    solution(Id, SolutionId),
    value(Arg, Input) : input(SolutionId, Arg, Input);
    tuple_size(Arg, Size) : input_tuple_size(SolutionId, Arg, Size);
    set_value(Arg, IncludedValue) : set_input_include(SolutionId, Arg, IncludedValue);
    not set_value(Arg, ExcludedValue) : set_input_exclude(SolutionId, Arg, ExcludedValue).

payload_copy(Id, Source) :- complex_solution(Id, SolutionId), output(SolutionId, Source).