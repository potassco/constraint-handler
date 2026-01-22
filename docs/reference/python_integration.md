# Python Integration

This page describes how to integrate Python code within the system.

---

## Expressions

In order to run Python expressions, the `python` operator is used.

Unlike other operators that are defined by a single keyword, the `python` operator has itself an argument and is represented by the `python/1` symbol.

```prolog
python(String)
```

| Name | Description |
| :--- | :--- |
| `String` | A [String] containing a callable Python function to be executed. |

Since this is an operator, the arguments to be passed to the Python function are expected to be provided by the
Operation using the operator.

### Existing Functions
The Python function provided in the `String` argument can be any valid Python function that is accessible in the
environment where the system is running.

One of the modules the environment provides by default is the `math` module, which includes a variety of mathematical functions.

!!! Example
    To compute the square root of `16` using the `sqrt` function from the `math` module, and assigning the result to the variable `x` you would declare:

    ```prolog
    variable_define(
        python_sqrt, 
        x, 
        operation(python("math.sqrt"), (val(int, 16), ()))
    ).
    ```

    This will yield the following result:

    ```prolog
    value(x,val(float,float("4.0")))
    ```

### Custom Functions
To use custom Python functions, you need to ensure that the function is defined in the Python environment where the system is running.


#### Lambda Functions
Lambda functions can be defined directly within the `String` argument of the `python` operator.

!!! Example
    To compute the cube of a number using a lambda function, you would declare:

    ```prolog
    variable_define(
        python_cube, 
        y, 
        operation(python("lambda x: x ** 3"), (val(int, 3), ()))
    ).
    ```

    This will yield the following result:

    ```prolog
    value(y,val(int,27))
    ```

#### Named Functions
To use named custom functions, you need to ensure that the function is passed to the Python environment before executing the operation.

Currently, this can be done by manipulating the `_shared_environment` of the constraint handlers `evaluator`.

!!! Example
    Assuming you have a Python function defined as follows:

    ```python
    def custom_function(x, y):
        return x * y + 10
    ```

    You would add this function to the `_shared_environment` before executing the operation:

    ```python
    import constraint_handler.evaluator as evaluator
    evaluator._shared_environment["custom_function"] = custom_function
    ```

    Then, you can use this function in your operation:

    ```prolog
    variable_define(
        custom_op, 
        z, 
        operation(python("custom_function"), (val(int, 5), (val(int, 3), ())))
    ).
    ```

    This will yield the following result:

    ```prolog
    value(z,val(int,25))
    ```