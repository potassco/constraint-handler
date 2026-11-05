%%% native expressions are keyed by their own term

native_expression(Expr) :- expr(Expr), engine(native, Expr).

%%% constants and variable references need no rules: a root is its own subject
%%% and the constant and variable rules below already derive its payload.

%%% constants
set_constant(set(Elements)) :- constant(set(Elements)).
tuple_constant(T) :- constant_tuple_size(T, _).
value(T, T) :- constant(T), not set_constant(T), not tuple_constant(T).
value(T, set) :- set_constant(T).
value(T, tuple) :- tuple_constant(T).
set_value(T, Value) :- constant_set_value(T, Value).
tuple_size(T, Size) :- constant_tuple_size(T, Size).
value(__tuple(T, Index), Value) :- constant_tuple_item(T, Index, Value).

%%% candidates and selection

variable_candidate(Name, Expr) :-
    variable_define(Name, Expr, Condition, _),
    value(Expr, _),
    value(Condition, boolean(true)).
variable_candidate(Name, Expr) :-
    variable_choose(Name, Expr, Condition, _),
    value(Expr, _),
    value(Condition, boolean(true)).

variable_selected(Name, Expr) :- variable_define(Name, Expr, _, _),
    variable_candidate(Name, Expr).
{ variable_selected(Name, Expr) } :- variable_choose(Name, Expr, _, _),
    variable_candidate(Name, Expr).

copy_value_from_to(Expr, variable(Name)) :- variable_selected(Name, Expr).

% a candidate whose payload matches the variable is selected with it
variable_selected(Name, Expr) :- variable_candidate(Name, Expr),
    not payload_difference(Name, Expr).
:- variable_selected(Name, Expr), payload_difference(Name, Expr).

% the variable payload is the union of selected payloads, so it holds one value per subject
:- variable_selected(Name, _), 2 { value(variable(Name), Value) : value(variable(Name), Value) }.
:- variable_selected(Name, _), 2 { tuple_size(variable(Name), Size) : tuple_size(variable(Name), Size) }.
:- variable_selected(Name, _), tuple_size(variable(Name), Size), Index = 0..Size-1,
    2 { value(__tuple(variable(Name), Index), Value) : value(__tuple(variable(Name), Index), Value) }.

payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    value(Expr, Value), not value(variable(Name), Value).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    set_value(variable(Name), Member), not set_value(Expr, Member).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    set_value(Expr, Member), not set_value(variable(Name), Member).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    tuple_size(Expr, Size), not tuple_size(variable(Name), Size).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    tuple_size(variable(Name), Size), not tuple_size(Expr, Size).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    tuple_size(Expr, Size), Index = 0..Size-1,
    value(__tuple(Expr, Index), Value), not value(__tuple(variable(Name), Index), Value).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    tuple_size(Expr, Size), Index = 0..Size-1,
    set_value(__tuple(variable(Name), Index), Member), not set_value(__tuple(Expr, Index), Member).
payload_difference(Name, Expr) :- variable_candidate(Name, Expr),
    tuple_size(Expr, Size), Index = 0..Size-1,
    set_value(__tuple(Expr, Index), Member), not set_value(__tuple(variable(Name), Index), Member).


%%% default ?

%%% set variables

set_variable(Name) :- set_contain_choose(Name, _, _, _).
set_variable(Name) :- set_contain(Name, _, _, _).
set_variable(Name) :- set_contain_default_to(Name, _, _, _, _).
value(variable(Name), set) :- set_variable(Name).

set_value(variable(Name), Value) :-
    set_contain(Name, Expr, Condition, _),
    value(Expr, Value),
    value(Condition, boolean(true)).

{ set_value(variable(Name), Value) } :-
    set_contain_choose(Name, Expr, Condition, _),
    value(Expr, Value),
    value(Condition, boolean(true)).


%%% constraints

:- ensure(Expr, _), not value(Expr, boolean(true)).
:- check(Expr, _), value(Expr, Value), Value != boolean(true).
