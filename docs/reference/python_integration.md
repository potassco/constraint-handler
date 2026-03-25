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
        z,
        operation(python("custom_function"), (val(int, 5), (val(int, 3), ())))
    ).
    ```

    This will yield the following result:

    ```prolog
    value(z,val(int,25))
    ```
---

## Statements
The constraint handler also supports using Python [Statements]. For this, the `statement_python/1` function symbol is used.

```prolog
statement_python(String)
```

| Name | Description |
| :--- | :--- |
| `String` | A [String] containing a Python statement to be executed. |

!!! Note "String Identifiers Required"
    To access a [Variable] from the current [Valuation] inside a Python [Statement], the variable must be defined using a string identifier (e.g., `"x"`), not a symbolic atom (e.g., `x`).

    The constraint handler automatically maps these string identifiers to Python variables.

    For example:
    ```prolog
    statement_python("y = x + 1")
    ```
    This statement expects a variable named `"x"` in the current valuation and adds or manipulates a variable named `"y"` in the resulting valuation.

!!! Important "Important: "x" vs x"
    Variables defined with string names (e.g., `"x"`) are completely distinct from variables defined with symbolic names (e.g., `x`).


!!! Example
    Imagine some variable `x` with an initial value of `5` that is supposed to be an input variable to an execution manipulating it by adding `1` twice using Python statements.

    Declaring the input variable:
    ```prolog
    variable_define(execution_input(python_add_twice, "x"),val(int,5)).
    ```

    Declaring the execution using a python statement `x = x + 1`:
    ```prolog
    execution_declare(python_add_twice, S, ("x",()), ("x",())) :-
        ADD_ONE = statement_python("x = x + 1"),
        S = seq2(
            ADD_ONE,
            ADD_ONE
        ).
    ```

    Executing the program:
    ```prolog
    execution_run(python_add_twice).
    ```

    This will yield the following result:
    ```prolog
    value(execution_output(python_add_twice,"x"),val(int,7))
    ```
### Variable Mapping
Given the current way Python statements expect variables to be defined using string identifiers, it may become quite cumbersome to work with these variables throughout the entire program.

Since only the Python statements require this format, a convenient way to map between symbolic variable names and string identifiers is to use assignment statements.

!!! Example
    Continuing from the previous example, to avoid using string identifiers throughout the entire program, you can use assignment statements to map between symbolic variable names and string identifiers.

    Define the input variables to the statement:
    ```prolog
    variable_define(execution_input(python_add_twice, x),val(int,5)).
    ```

    To deal with the mapping, assignments can be used like so:
    ```
    SYM_TO_STR = assign("x", variable(x))
    STR_TO_SYM = assign(x, variable("x"))
    ```

    Using these, the execution can be written as:
    ```prolog
    execution_declare(python_add_twice, S, (x,()), (x,())) :-
        SYM_TO_STR = assign("x", variable(x)),
        STR_TO_SYM = assign(x, variable("x")),
        ADD_ONE = statement_python("x = x + 1"),
        S = seq2(SYM_TO_STR, seq2(ADD_ONE, seq2(ADD_ONE, STR_TO_SYM))).
    ```

    Executing the program:
    ```prolog
    execution_run(python_add_twice).
    ```

    This will yield the following result:
    ```prolog
    value(execution_output(python_add_twice,x),val(int,7))
    ```
