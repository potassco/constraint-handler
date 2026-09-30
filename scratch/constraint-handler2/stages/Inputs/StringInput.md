## Information

A simple layer that takes a string of python input and converts into either
[PythonInput](PythonInput.md) or [InternalInput](InternalInput.md)

## ASP Format

## Python Datastructure

```python

def from_python(input_string: str, input_types: dict, output_types: dict)

# Parse the input expression and convert it into the appropriate input representation.
obj = from_python("result = x + 1", {"x": int}, {"result": int})
```

## TODO

- make return values explicit once decided
- what about error/warning communication
- need to add handling of external functions
