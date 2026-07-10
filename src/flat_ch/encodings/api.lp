% 
% This module contains the public facing API.
% 

% All predicates defined here are intended to be used directly by external users. To differentiate them
% from internal implementation details, all internal predicates are prefixed with '_fch_' and should not
% be used outside of the internal encoding modules.
%
% This also means that this is the only file that should contain unprefixed predicates! 
%
% For output predicates, this is the only file that should contain rules that derive unprefixed predicates. 
% For input predicates, this is the only file that should contain rules that consume unprefixed predicates. 

% =============================================================================
% SPECIAL INPUT
%
% This may be removed later since I don't really want to support statements.
% But right now I try to eliminate them via SSA.
% =============================================================================
#defined execution_declare/4.
_fch_ssa(execution_declare(NAME, STATEMENTS, INPUT, OUTPUT)) :- execution_declare(NAME, STATEMENTS, INPUT, OUTPUT).

% =============================================================================
% INPUT
% =============================================================================

%*! variable_define(Name, Expression)

Defines a variable by associating it with a specific expression that can be evaluated to yield its value.

Args:
 - Name: The unique identifier for the variable being defined.
 - Expression: The expression that computes the variable's value, which can include operations, 
    references to other variables, or literal values.
*%
#defined variable_define/2.
_fch_input(variable_define(NAME, EXPR))  :- variable_define(NAME, EXPR).

%*! variable_declare(Name)
Declares a dynamic variable.

This requires a domain to be assigned via variable_domain/2 before it can be resolved to a concrete value.

Args:
 - Name: The unique identifier for the dynamic variable.
*%
#defined variable_declare/1.
_fch_input(variable_declare(NAME))       :- variable_declare(NAME).

%*! variable_domain(Name, Expression)

Adds an expression to the domain of a previously declared variable.

Args:
 - Name: The unique identifier for the target variable.
 - Expression: The expression that evaluates to a value for the variable.
*%
#defined variable_domain/2.
_fch_input(variable_domain(NAME, EXPR))  :- variable_domain(NAME, EXPR).

%*! variable_declareOptional(Name)

Shortcut for `variable_domain(Name, val(none, none))`.

Args:
 - Name: The unique identifier for the target variable.
*%
#defined variable_declareOptional/1.
_fch_input(variable_domain(NAME, val(none, none))) :- variable_declareOptional(NAME).
_fch_input(variable_declare(NAME)) :- variable_declareOptional(NAME).

%*! ensure(Expression)

Defines an anonymous boolean constraint that must be satisfied for the solution to be valid. 

Args:
 - Expression: A boolean expression that represents the constraint to be enforced.
*%
#defined ensure/1.
_fch_input(ensure(__anonymous, EXPR))    :- ensure(EXPR).

%*! ensure(Name, Expression)

Defines a named boolean constraint that must be satisfied for the solution to be valid. 
The expression should evaluate to true for the constraint to hold.

Args:
 - Expression: A boolean expression that represents the constraint to be enforced on the solution space.
*%
#defined ensure/2.
_fch_input(ensure(NAME, EXPR))           :- ensure(NAME, EXPR).

%*! bool_evaluate(Expression)

Evaluates a boolean expression and exposes its result as `bool_evaluated(Expression, Value)`.

Args:
 - Expression: A boolean expression whose result should be materialized as a public helper atom.
*%
#defined bool_evaluate/1.
_fch_input(bool_evaluate(EXPR, EXPR))    :- bool_evaluate(EXPR).

%*! bool_evaluate(Label, Expression)

Evaluates a boolean expression and exposes its result as `bool_evaluated(Expression, Value)`.
The label is accepted for old-CH style parity but does not affect semantics.

Args:
 - Label: Ignored semantic label kept for compatibility.
 - Expression: A boolean expression whose result should be materialized as a public helper atom.
*%
#defined bool_evaluate/2.
_fch_input(bool_evaluate(EXPR, EXPR))    :- bool_evaluate(_, EXPR).

%*! set_declare(SetName)

Declares a set variable.

Args:
 - SetName: The unique identifier for the set being declared.
*%
#defined set_declare/1.
_fch_input(set_declare(NAME))            :- set_declare(NAME).

%*! set_baseDomain(SetName, Expression)
Statically defines the full background pool of allowed candidates for a specific set asset.
Args:
 - SetName: The identifier string for the targeted collection asset.
 - Expression: The background literal generation bounds expression.
*%
#defined set_baseDomain/2.
_fch_input(set_baseDomain(NAME, EXPR))   :- set_baseDomain(NAME, EXPR).

%*! set_assign(SetName, Expression)
Explicitly assigns concrete elements to a target set, constraining variable membership choices.
Args:
 - SetName: The identifier string for the targeted collection asset.
 - Expression: The literal element or structural set operation to enforce assignment.
*%
#defined set_assign/2.
_fch_input(set_assign(NAME, EXPR))       :- set_assign(NAME, EXPR).


#defined optimize_maximizeSum/3.
_fch_input(optimize_maximizeSum(EXPR,ELEMENT,PRIORITY)) :- optimize_maximizeSum(EXPR,ELEMENT,PRIORITY).

#defined optimize_precision/1.
#defined optimize_precision/2.
_fch_input(optimize_precision(EXPR)) :- optimize_precision(EXPR).
_fch_input(optimize_precision(EXPR,PRIORITY)) :- optimize_precision(EXPR,PRIORITY).

% =============================================================================
% OUTPUT
%
% This does not contain the entire output as many of the output rules
% have to be created for all types. Thus, most of the output rules can be
% found in the `generated/output.lp` file.
%
% =============================================================================

%*! value(Name, Type, Value)

Provides the final resolved value for a given variable identifier.

Args:
 - Name: The unique identifier of the variable whose value is being queried.
 - Type: The type of the variable's value, such as int, bool, set, etc.
 - Value: The concrete value assigned to the variable.
*%

%*! set_size(Name, Size)
The size of a set variable.

Args:
 - Name: The unique identifier of the set.
 - Size: The total number of elements contained within the set.
*%
% Declared sets get their size directly
set_size(NAME, SIZE)           :- _fch_set_decl(NAME), _fch_set_size(NAME, SIZE).
% Variables defined as sets get their size from the target set definition
set_size(VAR_NAME, SIZE)       :- _fch_var_def(VAR_NAME, TARGET_ID), _fch_set_decl(TARGET_ID), _fch_set_size(TARGET_ID, SIZE).

%*! bool_evaluated(Expression, Value)

Materialized result of a `bool_evaluate` request.

Args:
 - Expression: The original boolean expression that was requested.
 - Value: Either `val(bool,true)`, `val(bool,false)`, or `bad` if evaluation failed.
*%
bool_evaluated(EXPR, val(bool, true)) :-
    _fch_bool_evaluate(EXPR, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, true).

bool_evaluated(EXPR, val(bool, false)) :-
    _fch_bool_evaluate(EXPR, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, false).

bool_evaluated(EXPR, bad) :-
    _fch_bool_evaluate(EXPR, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

%*! evaluated(Operator, Arguments, Value)

Materialized result of an `evaluate` request.

Args:
 - Operator: The requested operator symbol.
 - Arguments: The original CH-style argument tuple.
 - Value: The resulting value, or `bad` if evaluation failed.
*%
evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_none_id, VALUE),
    TYPE = none.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_int_id, VALUE),
    TYPE = int.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_float_id, VALUE),
    TYPE = float.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_string_id, VALUE),
    TYPE = string.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_bool_id, VALUE),
    TYPE = bool.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_set_id, VALUE),
    TYPE = set.

evaluated(OP, ARGS, val(TYPE, VALUE)) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_dict_id, VALUE),
    TYPE = dict.

evaluated(OP, ARGS, bad) :-
    _fch_evaluate(OP, ARGS, EXPR_ID),
    _fch_dynamic_expr_val(EXPR_ID, _fch_type_fail_id, _).

%*! set_member(Name, Type, Value)

A specific element that is a member of a set.

Args:
 - Name: The unique identifier of the set.
 - Type: The type of the element, such as int, bool, etc.
 - Value: The concrete value of the element that is a member of the set.
*%