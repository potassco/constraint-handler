## Information

A simple layer that takes a string of python input and converts into either
[PythonInput](PythonInput.md) or [InternalInput](InternalInput.md)

## ASP Format

## Python Datastructure

```python
from python_input import Expr


def to_expression(input_string: str) -> Expr:
    # Convert a string of Python input into an expression
    ...

# instead of
#store = ConstraintStore()
#store.variable_declare(VariableRef("x"), VariableKind.regular, (1, 2))
#store.variable_declare(VariableRef("result"), VariableKind.regular, None)#
# you could write
#store.variable_define(VariableRef("result"), to_expression("x + 1"))
```

## TODO

- make return values explicit once decided
- what about error/warning communication
- need to add handling of external functions
