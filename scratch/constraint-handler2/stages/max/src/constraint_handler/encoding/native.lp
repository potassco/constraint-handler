%%% native expressions

native_expression(Id, Expr) :- expr(Id, Expr), engine(native, Id).

%%% constants
set_constant(set(Elements)) :- constant(set(Elements)).
value(T, T) :- constant(T), not set_constant(T).
value(T, set) :- set_constant(T).
set_value(T, Value) :- constant_set_value(T, Value).

value(Id, Value) :- native_expression(Id, Expr), value(Expr, Value).
set_value(Id, Value) :- native_expression(Id, Expr), set_value(Expr, Value).

%%% defines

variable_value(Name, ExprId) :-
    variable_define(Name, ExprId, ConditionId, Label),
    value(ExprId, _),
    value(ConditionId, boolean(true)).

value(variable(Name), Value) :- variable_value(Name, ExprId), value(ExprId, Value).
set_value(variable(Name), Value) :- variable_value(Name, ExprId), set_value(ExprId, Value).

%%% choose

% sets
variable_set_choice(Name, ExprId) :- variable_choose(Name, ExprId, ConditionId, Label),
    value(ExprId, set),
    value(ConditionId, boolean(true)).

{ variable_value(Name, ExprId) } :- variable_set_choice(Name, ExprId).

% ensure that we do not select only a subset or superset
variable_set_difference(Name, ExprId) :- variable_set_choice(Name, ExprId),
    set_value(ExprId, Value), not set_value(variable(Name), Value).
variable_set_difference(Name, ExprId) :- variable_set_choice(Name, ExprId),
    set_value(variable(Name), Value), not set_value(ExprId, Value).

variable_value(Name, ExprId) :- variable_set_choice(Name, ExprId),
    value(variable(Name), set), not variable_set_difference(Name, ExprId).

% integer, real, string, etc....
{ value(variable(Name), Expr) } :- variable_choose(Name, ExprId, ConditionId, Label),
    value(ExprId, Expr), Expr != set,
    value(ConditionId, boolean(true)).


%%% default ?

%%% at most one value per variable

variable(Name) :- variable_choose(Name, _, _, _).
variable(Name) :- variable_define(Name, _, _, _).
variable(Name) :- variable_default_to(Name, _, _, _, _).

:- variable(Name), 2 { value(variable(Name), Expr) : value(variable(Name), Expr) }.

:- variable_value(Name, ExprId), value(ExprId, set),
    set_value(variable(Name), Value), not set_value(ExprId, Value).

%%% set variables

set_variable(Name) :- set_contain_choose(Name, _, _, _).
set_variable(Name) :- set_contain(Name, _, _, _).
set_variable(Name) :- set_contain_default_to(Name, _, _, _, _).
value(variable(Name), set) :- set_variable(Name).

set_value(variable(Name), Value) :-
    set_contain(Name, ExprId, ConditionId, Label),
    value(ExprId, Value),
    value(ConditionId, boolean(true)).

{ set_value(variable(Name), Value) } :-
    set_contain_choose(Name, ExprId, ConditionId, Label),
    value(ExprId, Value),
    value(ConditionId, boolean(true)).


%%% constraints

:- ensure(Id, _), not value(Id, boolean(true)).
:- check(Id, _), value(Id, Value), Value != boolean(true).
