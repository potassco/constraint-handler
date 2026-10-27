complex_solution(Id, SolutionId) :-
    engine(complex, Id),
    solution(Id, SolutionId),
    value(Arg, Input) : input(SolutionId, Arg, Input);
    set_value(Arg, IncludedValue) : set_input_include(SolutionId, Arg, IncludedValue);
    not set_value(Arg, ExcludedValue) : set_input_exclude(SolutionId, Arg, ExcludedValue).

value(Id, Value) :- complex_solution(Id, SolutionId), output(SolutionId, Value).
set_value(Id, Value) :- complex_solution(Id, SolutionId), set_output(SolutionId, Value).