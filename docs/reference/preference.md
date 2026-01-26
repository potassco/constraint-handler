# Preference
This page documents how to declare and use preferences in the constraint handler.

In [Optimization], we have shown how to declare optimization objectives such that the solver tries to find solutions that minimize or maximize certain values. Ultimately, this leads to a single optimal solution.

However, sometimes we may not want only the best solution but also the second or even third best solution. More precisely, we may want the solutions to have an ordering based on our preferences.

---

## Declaring Preferences
The constraint handler provides multiple ways of specifying preferences. Here, we will cover the different ways of declaring preferences using preference values and how to combine them to express more complex preferences.

### Variable Value
One way to provide a preference is to assign a preference value to a variable having a specific value. For this, we can use the `preference_variableValue/4` predicate.

```prolog
preference_variableValue(Identifier, Name, Expression, Value)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific preference. |
| `Name` | The name of the variable for which we are specifying a preference. |
| `Expression` | The expression representing the value of the variable we are assigning a preference to. |
| `Value` | The preference value assigned to the variable having the specified value. |

The preference value is a numeric value that indicates how much we prefer that variable to take that specific value. Higher preference values indicate stronger preferences.

For convenience, there also exists a shorthand version `preference_variableValue/3` where the `Value` is set to 1 by default.

!!! Example
    Consider a program that defines a variable `color` with possible values `red`, `green`, `blue`, and `yellow`.

    ```prolog
    variable_declare(declare_color, color, fromFacts).
    variable_domain(color, val(symbol, (red;green;blue;yellow))).
    ```

    If we want to express that we prefer `red` the most, followed by `blue` and `green`, and finally `yellow`, we can assign preference values as follows:

    ```prolog
    preference_variableValue(dummy,color,val(symbol,red),5).
    preference_variableValue(dummy,color,val(symbol,(green;blue)),3).
    preference_variableValue(dummy,color,val(symbol,yellow)).
    ```

    In this example, the variable `color` has the highest preference value of `5` for the value `red`, a preference value of `3` for both `green` and `blue`, and the lowest preference value of `1` for `yellow`. When the solver evaluates solutions, it will prioritize those where `color` is `red`, followed by those where it is `green` or `blue`, and lastly those where it is `yellow`.

    This leads to an ordering of solutions based on our specified preferences for the variable `color` with the highest values appearing first.

### Holds
In addition to assigning preference values to variable-value pairs, we can also express preferences based on certain conditions using the `preference_holds/3` predicate.

```prolog
preference_holds(Identifier, Condition, Value)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific preference. |
| `Condition` | An [Expression] representing the condition we are assigning a preference to. |
| `Value` | The preference value assigned when the condition holds true. |


!!! Example
    Taking the previous example further, suppose we want to express a preference for a combination of colors `color(a)` and `color(b)`.

    ```prolog
    variable_declare(declare_color, color(a;b), fromFacts).
    variable_domain(color(a;b), val(symbol, (red;green;blue;yellow))).
    ```

    If we wanted to express that we prefer combinations where `a` and `b` are equal, we could do so as follows:

    ```prolog
    preference_holds(bla, operation(eq, (variable(color(a)),(variable(color(b)),()))), 2).
    preference_holds(bla, operation(neq, (variable(color(a)),(variable(color(b)),())))).
    ```
    In this example, we express a preference value of `2` for the condition where `color(a)` is equal to `color(b)`. Additionally, we have a default preference (with an implicit value of `1`) for the condition where they are not equal.

    Thus, first models will appear where `color(a)` and `color(b)` are the same, followed by models where they differ.

### More Complex Preferences
Preferences can also be combined to create more complex preference structures. For instance, we can assign different preference values to multiple conditions or variable-value pairs.

!!! Example
    Continuing from the previous examples, suppose we want to combine the preferences of the variable `color` with the preference for `color(a)` and `color(b)` being equal.

    ```prolog
    variable_declare(declare_color, color(a;b), fromFacts).
    variable_domain(color(a;b), val(symbol, (red;green;blue;yellow))).

    preference_holds(bla, operation(eq, (variable(color(a)),(variable(color(b)),()))), 10).
    preference_variableValue(dummy,color(a;b),val(symbol,red),3).
    preference_variableValue(dummy,color(a;b),val(symbol,(green;blue)),2).
    preference_variableValue(dummy,color(a;b),val(symbol,yellow)).
    ```

    This describes both, a preference where `color(a)` and `color(b)` are equal, as well as individual preferences for the values of `color(a)` and `color(b)`.

---

## Preference Score
Declaring preference values is not enough. These values have to be aggregated into a total preference score for each model. This is done using the `preference_score/1` result predicate.

```
preference_score(TotalScore)
```

| Name | Description |
| :--- | :--- |
| `TotalScore` | The total aggregated preference score for the current model. |

!!! Example
    Using the values of the previous examples, the total preference score for a model where `color(a)` and `color(b)` are both `red` would be calculated as follows:

    - Preference for `color(a) = red`: 3
    - Preference for `color(b) = red`: 3
    - Preference for `color(a) = color(b)`: 10
    - Total Score: 3 + 3 + 10 = 16

### Negative Values
So far, we have only used positive preference values. However, it is also possible to use negative values to express that certain conditions or variable-value pairs are undesirable.

However, instead of decreasing the overall score, negative preference values will increase the score of models that do not satisfy the corresponding condition or variable-value pair.

!!! Example
    Extending the previous example, suppose we want to express that we strongly dislike the color `yellow` appearing in any model.

    ```
    variable_declare(declare_color, color(a;b), fromFacts).
    variable_domain(color(a;b), val(symbol, (red;green;blue;yellow))).

    preference_holds(bla, operation(eq, (variable(color(a)),(variable(color(b)),()))), 10).
    preference_variableValue(dummy,color(a;b),val(symbol,red),3).
    preference_variableValue(dummy,color(a;b),val(symbol,(green;blue)),2).
    preference_variableValue(dummy,color(a;b),val(symbol,yellow),-5).
    ```

    One might be inclined to believe that models containing yellow have `5` subtracted from their total score for each occurrence. This would lead the model containing the combination `color(a) = yellow` and `color(b) = yellow` to have a total score of `0`.

    However, this is not the case. Instead, models that do not contain yellow will have their total score increased by `5` for each occurrence of yellow that is avoided. Thus, the model with `color(a) = yellow` and `color(b) = yellow` will still have a total score of `10`, because it satisfies the preference of `color(a) = color(b)`. On the other hand, a model with `color(a) = red` and `color(b) = red` will have a total score of `26`, which is calculated as follows:

    - Preference for `color(a) = red`: 3
    - Preference for `color(a) != yellow`: 5
    - Preference for `color(b) = red`: 3
    - Preference for `color(b) != yellow`: 5
    - Preference for `color(a) = color(b)`: 10
    - Total Score: 3 + 5 + 3 + 5 + 10 = 26

---

## Maximize Score
To actually utilize the declared preferences and their scores, we also need to instruct the solver to consider these preference values when searching for solutions. This can be done using the `preference_maximizeScore/0` predicate.

!!! Warning
    When using preferences by running `Clingo` on the command line, it is currently necessary to also provide the `--heuristic=domain` option to ensure that the solver properly considers the preferences when generating models.

```prolog
preference_maximizeScore.
```

This prints the found models in descending order of their preference scores.
