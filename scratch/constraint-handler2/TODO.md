- defaults implementation
- hasValue should be isNotNone to avoid confusion with undefined
- figure out all places where kroco would need to change to adopt to new undefined variables behaviour
- propagator implementation
- float comparisons could be done linear with order encoding instead of quadratic
- rename complex to table-constraints
- value(__table(Expr, Index), 42) vs set_value(Expr, value)    Either decode sets differently or decode tuples differently, does this work with sets inside tuples? What about value(__set(Expr), Value) -> No, several values per Expr

payload crap, also multiple defintions and choices active at the same time are hard to encodine in a linear way!.
One Variable can have a huge domain, so a lot of expressions that can or can't overlap with each other need to be considered, making the encoding complex and potentially inefficient.
Facts:
- several definitions can be true at once
  - if they give two different values, it created a conflict
  - in case of sets its not that easy, as sets can have overlapping elements without causing a conflict
    - how to solve this?
    (extra check, if definition target has a set value that is not in the source)
    - what about sets inside tuples

    a = (41, {1})
    a = (41, {1, 2})
    what are the facts/how to detect that conflict
  - if there is a definition, no choices should be made active, as they would need to agree and could also be omitted. Important to not have multiple models
  



- use copy_value_from_to(Expr1, Expr2)
