%*! type_variable(Scope, Variable, Type)
The type of a variable existing in some scope.

Args:
    - Scope: The scope in which the variable exists.
    - Variable: The name of the variable.
    - Type: The type of the variable.
*%

%*! type_expression(Scope, Expression, Type)
The type of an expression in some scope.

Args:
    - Scope: The scope in which the expression exists.
    - Expression: The expression to be typed.
    - Type: The type of the expression.
*%

%*! operator_declare(Operator, InputTypes, ReturnType)

Valid input and return types for an operator.

Args:
    - Operator: The name of the operator.
    - InputTypes: The list of input types for the operator.
    - ReturnType: The return type of the operator.
*%

%*! operator_declare_variadic(Operator, InputType, ReturnType, Rank)

Valid input and return types for a variadic operator.

Variadic operators use a ranking system in order to determine the return type
based on the input types. If inputs of different types are encountered,
the operator will return the type corresponding to the return type with the highest rank.

Args:
    - Operator: The name of the operator.
    - InputType: The input type for the operator.
    - ReturnType: The return type of the operator.
    - Rank: The rank of the return type for this operator.
*%

%*! _type(Symbol)

Declares a symbol as a type.

Args:
    - Symbol: The symbol declared as a type.
*%