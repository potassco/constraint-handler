# constraint_handler

The constraint handler is a clingo library that supports solving discrete combinatorial decision or optimization problems where constraints and variables are defined through expressions.

## Installation
This project requires Python `3.12+` and can be installed either from TestPyPI or directly from source.
### From TestPyPI
This is the easiest way to get started. Run the following command in your terminal:
```bash
pip install -i https://test.pypi.org/simple/ constraint-handler
```
### From Source (for Developers)
To install the project for development, clone the repository and install it in editable mode.

```bash
git clone https://github.com/potassco/constraint-handler
cd constraint-handler
pip install -e .
```
## Documentation
To generate and open the documentation, run

```bash
nox -s doc -- serve
```

Instructions to install and use `nox` can be found in
[DEVELOPMENT.md](./DEVELOPMENT.md)
