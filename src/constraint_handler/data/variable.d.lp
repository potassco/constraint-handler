%*! variable_declare(Label, Name, Domain)

Declares a variable together with the source of its domain.

The declaration itself does not assign one concrete value. Instead, it states
that the variable may take one value from the domain described by `Domain`.

Args:
    - Label: The optional [Label] attached to the declaration.
    - Name: The name of the variable being declared.
    - Domain: A domain descriptor such as `fromFacts`, `fromList(...)`, or `boolDomain`.
*%

%*! variable_declare(Name, Domain)

Shorthand for [variable_declare/3] using an anonymous label.

Args:
    - Name: The name of the variable being declared.
    - Domain: A domain descriptor such as `fromFacts`, `fromList(...)`, or `boolDomain`.
*%

%*! variable_declareOptional(Label, Name)

Declares a variable as optional.

Optional variables automatically receive the value `val(none,none)` as part of
their domain and can therefore be considered as either assigned or unassigned in different models.

Args:
    - Label: The optional [Label] attached to the declaration.
    - Name: The name of the optional variable.
*%

%*! variable_declareOptional(Name)

Shorthand for [variable_declareOptional/2] using an anonymous label.

Args:
    - Name: The name of the optional variable.
*%

%*! variable_define(Label, Name, Expression)

Defines a variable through one expression.

In contrast to [variable_declare/3], this does not create alternatives across
models. Instead, the variable receives exactly the valuation of `Expression`.

Args:
    - Label: The optional [Label] attached to the definition.
    - Name: The name of the variable being defined.
    - Expression: The [Expression] whose valuation becomes the variable value.
*%

%*! variable_define(Name, Expression)

Shorthand for [variable_define/3] using an anonymous label.

Args:
    - Name: The name of the variable being defined.
    - Expression: The [Expression] whose valuation becomes the variable value.
*%

%*! variable_domain(Label, Name, Expression)

Provides one domain contribution for a declared variable.

This predicate is used together with `variable_declare(..., fromFacts)`.
Each matching `variable_domain` fact contributes one possible value to the
variable's domain.

Args:
    - Label: The optional [Label] attached to the domain fact.
    - Name: The name of the variable whose domain is extended.
    - Expression: The [Expression] contributing one or more candidate values.
*%

%*! variable_domain(Name, Expression)

Shorthand for [variable_domain/3] using an anonymous label.

Args:
    - Name: The name of the variable whose domain is extended.
    - Expression: The [Expression] contributing one or more candidate values.
*%