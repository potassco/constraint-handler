%*! execution_declare(Label, Name, Statement, Inputs, Outputs)

Declares one named execution.

The statement describes how an input valuation is transformed into an output
valuation. The input and output variables are given as recursive lists of names.

Args:
    - Label: The optional [Label] attached to the declaration.
    - Name: The identifier of the execution.
    - Statement: The [Statement] implementing the transformation.
    - Inputs: A list of input variable names.
    - Outputs: A list of output variable names.
*%

%*! execution_declare(Name, Statement, Inputs, Outputs)

Shorthand for [execution_declare/5] using an anonymous label.

Args:
    - Name: The identifier of the execution.
    - Statement: The [Statement] implementing the transformation.
    - Inputs: A list of input variable names.
    - Outputs: A list of output variable names.
*%

%*! execution_run(Label, Name)

Requests the execution of a previously declared execution.

Args:
    - Label: The optional [Label] attached to the run declaration.
    - Name: The identifier of the execution that should be run.
*%

%*! execution_run(Name)

Shorthand for [execution_run/2] using an anonymous label.

Args:
    - Name: The identifier of the execution that should be run.
*%