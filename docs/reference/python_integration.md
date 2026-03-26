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

This can be done by passing the desired environment into the `add_to_control` function during initialization of the constraint handler.

!!! Example
    Assuming you have a Python function defined as follows:

    ```python
    def custom_function(x, y):
        return x * y + 10
    ```

    You would add this function to a dictionary representing the environment and pass it to the `add_to_control` function:

    ```python
    my_environment = {"my_function": custom_function}
    constraint_handler.add_to_control(control, environment=my_environment)
    ```

    Then, you can use this function in your operation using the identifier you provided in the environment:

    ```prolog
    variable_define(
        z,
        operation(python("my_function"), (val(int, 5), (val(int, 3), ())))
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

### Solver Environment
The `statement_python/1` function symbol also has access to the solver environment, which provides additional functionality directly related to the constraint solving process.

#### FailIntegrityExn
One of the features available in the solver environment is the ability to raise a `FailIntegrityExn` exception.

This is a special exception that, when raised within a Python statement, does not crash or create a warning. Instead, it resembles a violation of an integrity constraint.

!!! Example
    In the following program, we specify two input variables `x` and `y` with a domain of `1..3`. The execution divides `x` by `y` and assigns the result to `z`. If `z` is less than or equal to `1.5`, it raises a `FailIntegrityExn`.

    ```prolog
    variable_declare(execution_input(py_exn, ("x";"y")), fromFacts).
    variable_domain(execution_input(py_exn, ("x";"y")), val(int, 1..3)).

    execution_declare(py_exn, S, ("x",("y",())),("z",())) :-
        S = statement_python("z = x/y\nif z <= 1.5:\n  raise solver_environment.FailIntegrityExn").

    execution_run(py_exn).
    ```

    This means, all values where `x` = 1 will automatically violate the integrity constraint. Likewise, whenever `y` is 2 or 3, there is no way for `z` to be greater than `1.5`. The only values that satisfy the integrity constraint are when `x` is 2 or 3 and `y` is 1, which results in `z` being 2 or 3, respectively.

    The output of this program will be two models that satisfy the integrity constraint:
    ```prolog
    value(execution_input(py_exn,"y"),val(int,1))
    value(execution_input(py_exn,"x"),val(int,2))
    value(execution_output(py_exn,"z"),val(float,float("2.0")))
    ```
    and
    ```prolog
    value(execution_input(py_exn,"y"),val(int,1))
    value(execution_input(py_exn,"x"),val(int,3))
    value(execution_output(py_exn,"z"),val(float,float("3.0")))
    ```

#### Constrain
To make it more convenient to raise a `FailIntegrityExn` exception, the solver environment also provides a `constrain` function.

This function takes a boolean condition as an argument and raises a `FailIntegrityExn` if the condition is not satisfied.

!!! Note
    Here, booleans are evaluated in the Pythonic way, meaning not just `False` is considered false, but also `None`, `0`, empty collections, etc.

!!! Example
    The example used in the previous section can be rewritten using the `constrain` function as follows:

    ```prolog
    variable_declare(execution_input(py_exn, ("x";"y")), fromFacts).
    variable_domain(execution_input(py_exn, ("x";"y")), val(int, 1..3)).

    execution_declare(py_exn, S, ("x",("y",())),("z",())) :-
        S = statement_python("z = x/y\nsolver_environment.constrain(z > 1.5)").

    execution_run(py_exn).
    ```

    >Since the `constrain` function raises a `FailIntegrityExn` when the condition is not satisfied, we had to reverse the condition from `z <= 1.5` to `z > 1.5` in order to maintain the same integrity constraint as in the previous example.

    This will yield the same result as the previous example, which are the two models that satisfy the integrity constraint:
     ```prolog
    value(execution_input(py_exn,"y"),val(int,1))
    value(execution_input(py_exn,"x"),val(int,2))
    value(execution_output(py_exn,"z"),val(float,float("2.0")))
    ```
    and
    ```prolog
    value(execution_input(py_exn,"y"),val(int,1))
    value(execution_input(py_exn,"x"),val(int,3))
    value(execution_output(py_exn,"z"),val(float,float("3.0")))
    ```
