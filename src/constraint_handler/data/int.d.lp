%*! _int_add(Expression, Index, Value)

Computation helper for addition.

This predicate recursively computes the sum of a variadic number of arguments for the `add` operator.
It uses the index to keep track of how many arguments have been summed so far, and the value to
keep track of the current sum.

Args:
    - Expression: The [Expression] representing the operation to be computed.
    - Index: The index of the argument in the computation (starting from 0).
    - Value: The [Expression] assigned as the value of the sum of the arguments up to the specified index.
*%

%*! _int_mult(Expression, Index, Value)

Computation helper for multiplication.

This predicate recursively computes the product of a variadic number of arguments for the `mult` operator.
It uses the index to keep track of how many arguments have been multiplied so far, and the value to
keep track of the current product.

Args:
    - Expression: The [Expression] representing the operation to be computed.
    - Index: The index of the argument in the computation (starting from 0).
    - Value: The [Expression] assigned as the value of the product of the arguments up to the specified index.
*%
