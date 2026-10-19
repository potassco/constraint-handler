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
#store.choose_from_iterator(VariableRef("x"), (1, 2))
#store.choose(VariableRef("result"), None)#
# you could write
#store.define(VariableRef("result"), to_expression("x + 1"))
```

## TODO

- make return values explicit once decided
- what about error/warning communication
- need to add handling of external functions
