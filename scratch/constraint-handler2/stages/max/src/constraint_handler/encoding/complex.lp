complex_solution(Expr, SolutionId) :-
    %engine(complex, Expr) % makes grounding slow
    solution(Expr, SolutionId),
    value(Arg, Input) : input(SolutionId, Arg, Input);
    tuple_size(Arg, Size) : input_tuple_size(SolutionId, Arg, Size);
    set_value(Arg, IncludedValue) : set_input_include(SolutionId, Arg, IncludedValue);
    not set_value(Arg, ExcludedValue) : set_input_exclude(SolutionId, Arg, ExcludedValue).

copy_value_from_to(Out, Expr) :- complex_solution(Expr, SolutionId), output(SolutionId, Out).