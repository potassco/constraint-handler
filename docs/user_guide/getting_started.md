# Getting Started

!!! info
    Since **constraint_handler** is a library, it is intended to be used within your own projects and not as a standalone application.

This guide will help you get started with using the library in your Python projects or in your Clingo programss.

Make sure the **constraint_handler** is [installed][installation] as a dependency of your project. Additionally, ensure that you have [Clingo](https://potassco.org/clingo/) installed, as it is required for using the constraint_handler library.

## Adding to a Clingo program

The easiest way to use the library is to load it from a script section in a clingo program.
In the following example, this is done in the last 8 lines of the file.

```prolog
variable_define(some_name, x, val(int,42)).
#show value/2.

#script (python)
import constraint_handler

def main(ctrl):
    constraint_handler.add_to_control(ctrl)
    ctrl.ground()
    ctrl.solve()
#end.
```

    ```python
    from clingo.control import Control
    control = Control()
    ```
## Adding to Clingo Control Object in a Python program

The library can also be used from Python by adding it to a clingo control object.

1. Create a standard clingo control object:

    ```python
    from clingo.control import Control
    control = Control()
    ```

2. Add the import statement for the constraint_handler library:

    ```python
    import constraint_handler
    ```

3. Add the constraint handler to the clingo control object:

    ```python
    constraint_handler.add_to_control(control)
    ```

You can now use the constraint handler features within your clingo program.

## Test Example
To check whether the installation was successful, here is a small example:

```python
from clingo.control import Control
import constraint_handler
# Create a clingo control object
control = Control()
# Add the constraint handler to the control object
constraint_handler.add_to_control(control)
# Add a small example
control.add("base", [], """
variable_define(some_name, x, val(int,42)).
#show value/2.
""")
# Ground the program
control.ground([("base", [])])
# Solve the program
with control.solve(yield_ = True) as handle:
    for model in handle:
        print(model)
```
This should show a single model with only `value(x,val(int,42))` in the output.
