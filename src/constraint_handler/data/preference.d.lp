%*! preference_variableValue(Label, Name, Expression, Score)

Assigns a preference score to one variable having one specific value.

Args:
    - Label: The optional [Label] attached to the preference declaration.
    - Name: The variable whose value is being preferred.
    - Expression: The preferred value expression.
    - Score: The score contributed by this preference.
*%

%*! preference_variableValue(Name, Expression, Score)

Shorthand for [preference_variableValue/4] using an anonymous label.

Args:
    - Name: The variable whose value is being preferred.
    - Expression: The preferred value expression.
    - Score: The score contributed by this preference.
*%

%*! preference_variableValue(Name, Expression)

Shorthand for [preference_variableValue/3] with score `1`.

Args:
    - Name: The variable whose value is being preferred.
    - Expression: The preferred value expression.
*%

%*! preference_holds(Label, Expression, Score)

Assigns a preference score to a condition that should hold.

Positive scores reward models in which the expression evaluates to `true`, while
negative scores are compiled into a preference for the negated condition.

Args:
    - Label: The optional [Label] attached to the preference declaration.
    - Expression: The boolean [Expression] representing the preferred condition.
    - Score: The score contributed by this preference.
*%

%*! preference_holds(Expression, Score)

Shorthand for [preference_holds/3] using an anonymous label.

Args:
    - Expression: The boolean [Expression] representing the preferred condition.
    - Score: The score contributed by this preference.
*%

%*! preference_holds(Expression)

Shorthand for [preference_holds/2] with score `1`.

Args:
    - Expression: The boolean [Expression] representing the preferred condition.
*%

%*! preference_score(TotalScore)

The aggregated preference score of the current model.

Args:
    - TotalScore: The sum of all preference contributions active in the current model.
*%

%*! preference_maximizeScore

Enables search for models in descending order of their preference score.

When this fact is present, the solver is guided by preference-specific
heuristics and exposes the resulting total score through [preference_score/1].

*%