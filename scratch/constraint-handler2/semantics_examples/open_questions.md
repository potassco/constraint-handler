# Integration into the logic program

1. Is evaluate/1 allowed in the body? Will it be made true in a hybrid system
   way?
1. Is value/2 allowed in the body? This might lead to cycles.
1. Allow body usage but only as defined precisely in the logic program.

# Constraint handler internals

1. Are the statements in the examples enough to declare a variable? I(philW)
   think so.

# Further language elements

1. declare_variable(Name,Type) as a type checking mechanism with possible
   meaning:
   ```
   :- declare_variable(Name,Type), singleton(Variable), value(val(Type',_)), Type!=Type'.
   ```
