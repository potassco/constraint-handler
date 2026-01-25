# Knapsack

This example demonstrates how to solve the classic Knapsack Problem. It is intended to showcase a beginner friendly approach to modeling optimization problems in the constraint handler.

Below are some of the key predicates and function symbols used in this example. In case you are not familiar with them, please refer to the respective sections in the documentation linked below:

| Concept | Description |
| :--- | :--- |
| [variable_define] | Assigns a specific [Value] to a [Variable]. |
| [variable_declare] | Declares a [Variable] with a specific domain of possible [Values]. |
| [operation] | Defines an operation that can be used in [Expressions]. |
| [ensure] | Adds a requirement that must be satisfied in any valid solution. |
| [optimize_maximizeSum] | Defines an optimization objective to maximize the sum of specified [Expressions]. |

## Problem description
The Knapsack Problem is a combinatorial optimization problem where the goal is to maximize the total value of items placed in a knapsack without exceeding its weight capacity.

### The Rules

1. **Items:** You have a set of items, each with a specific **weight (kg)** and **profit (€)**.
2.  **Capacity:** The knapsack can hold a maximum of **5.0 kg**.
3.  **Objective:** Maximize the total **Value (€)** of the items in the knapsack.
4.  **Constraint:** You cannot take partial items; you must either take an item or leave it.

### The Items
We will use the following items for this example:

| ID | Weight | Value |
| :--- | :--- | :--- |
| 1 | 0.02 | 1200.0 |
| 2 | 0.15 | 300.0 |
| 3 | 0.8 | 850.0 |
| 4 | 2.4 | 1600.0 |
| 5 | 1.8 | 1100.0 |
| 6 | 3.5 | 1800.0 |
| 7 | 2.0 | 50.0 |
| 8 | 4.0 | 20.0 |

## Encoding
Here, we will take you through the process of encoding the Knapsack Problem using the constraint handler in a step-by-step manner. We will go from the data setup all the way to the output of the optimal solution.

!!! Note
    For simplicity, we will try to keep the encoding as straightforward as possible, avoiding advanced features and modeling techniques. The result may thus not be the most efficient encoding possible, but it should be easy to follow and understand.

### Data Setup
In this example, we will assume the input is provided as facts for the items together with the capacity of the knapsack:

```prolog
item(1, "0.02", "1200.0").
item(2, "0.15", "300.0").
item(3, "0.8",  "850.0").
item(4, "2.4",  "1600.0").
item(5, "1.8",  "1100.0").
item(6, "3.5",  "1800.0").
item(7, "2.0",  "50.0").
item(8, "4.0",  "20.0").
capacity("5.0").
```

Given this input, we will first transform the items and capacity into suitable variable definitions using [variable_define]

The capacity can be directly defined as a single float variable:
```prolog
variable_define(dummy, total_capacity, val(float, float(C))) :- capacity(C).
```

To transform the items into variable definitions, we will define two variables for each item: one for its weight and one for its value. We will use the item ID to uniquely identify each variable.

```prolog
variable_define(dummy, item_weight(ID), val(float, float(WEIGHT))) :- item(ID, WEIGHT, _).
variable_define(dummy, item_value(ID), val(float, float(VALUE))) :- item(ID, _, VALUE).
```

This concludes the data setup part of our encoding.

### Item Selection
Given our data setup, we now have to define how we want to select items to include in the knapsack. For this, we will [declare][variable_declare] a binary variable for each item indicating whether the item is included in the knapsack or not.

```prolog
variable_declare(dummy, item_included(ID), boolDomain) :- item(ID, _,_).
```

This defines `item_included(ID)` as a boolean variable for each item. Remember, while [variable_define] assigns a specific value to a variable, [variable_declare] declares a variable with a domain of possible values.

This means that `item_included(ID)` can take the values `false` (not included) or `true` (included) and either of these values can be chosen in a solution.

This single line is all we need for the item selection part of our encoding.

### Total Weight
Next, we need to calculate the total weight of the selected items to ensure it does not exceed the knapsack's capacity.

For this, we will use a custom predicate `weight/2` to recursively calculate the total weight based on the `item_included` variables.

```prolog
weight(ID, VALUE).
```

| Name | Description |
| :--- | :--- |
| `ID` | The item ID up to which we are calculating the total weight. |
| `VALUE` | The calculated total weight as a [Value]. |


First, we have to define the base case for our recursion, which is when no items are considered (ID = 0):
```prolog
weight(0, val(float, 0.0)).
```

Next, we define the recursive case.
```prolog
weight(N, NEXT) :-
    item(N, _, _),
    weight(N-1, PREV),
    COND = variable(item_included(N)),
    ADD = operation(add, (PREV,(variable(item_weight(N)),()))),
    NEXT = operation(ite, (COND, (ADD,(PREV,())))).
```
Let us go over each line of the recursive case:

1. `item(N, _, _)`: Retrieves the weight and value of the current item.
2. `weight(N-1, PREV)`: Retrieves the total weight calculated for all previous items.
3. `COND = variable(item_included(N))`: Here, `variable(item_included(N))` holds the value of the variable `item_included(N)`, which is either `true` or `false` and thus serves as the condition of whether the current item is included in the knapsack.
4. `ADD = operation(add, (PREV,(variable(item_weight(N)),())))`: Defines an addition operation that adds the weight of the current item to the previous total weight (`PREV`).
5. `NEXT = operation(ite, (COND, (ADD,(PREV,()))))`: Finally, we define `NEXT` as an if-then-else operation. If `COND` is true (the item is included), we take the result of the addition (`ADD`); otherwise, we keep the previous total weight (`PREV`).

In the next section, we will use this `weight/2` predicate to enforce the capacity constraint.

### Capacity
Now that we have a way to calculate the total weight of the selected items, we need to ensure that this total weight does not exceed the knapsack's capacity.

We can achieve this by using the [ensure] to add a constraint to our model:

```prolog
ensure(capacity_constraint, operation(leq, (TOTAL_WEIGHT,(variable(total_capacity),())))) :- weight(_, TOTAL_WEIGHT).
```

This line states that the `TOTAL_WEIGHT` calculated at any point must be less than or equal to the `total_capacity` variable we defined earlier.

Again, just a single line is sufficient to enforce the capacity constraint in our encoding.

### Optimization
Finally, we need to define our optimization objective, which is to maximize the total value of the selected items.

For this, we will use the [`optimize_maximizeSum/2`][optimize_maximizeSum] predicate as follows:

```prolog
optimize_maximizeSum(dummy, EXPR, ID) :- 
    item(ID, _, _),
    COND = variable(item_included(ID)),
    EXPR = operation(if, (COND, (variable(item_value(ID)),()))).
```

Explaining the lines:

1. `item(ID, _, _)`: Again, we look at each item by its ID.
2. `COND = variable(item_included(ID))`: Just like before, we retrieve the value of the `item_included(ID)` variable to use as a condition.
3. `EXPR = operation(if, (COND, (variable(item_value(ID)),())))`: Finally, based on the condition, we decide whether to include the item's value in the optimization sum or not.

This is enough to set up our optimization objective and complete the encoding of the Knapsack Problem.

## Result
Our encoding is now complete and should look similar to the following:

```prolog
% Data Setup
variable_define(dummy, total_capacity, val(float, float(C))) :- capacity(C).
variable_define(dummy, item_weight(ID), val(float, float(WEIGHT))) :- item(ID, WEIGHT, _).
variable_define(dummy, item_value(ID), val(float, float(VALUE))) :- item(ID, _, VALUE).

% Item Selection
variable_declare(dummy, item_included(ID), boolDomain) :- item(ID, _,_).

% Total Weight
weight(0, val(float, float("0.0"))).
weight(N, NEXT) :-
    weight(N-1, PREV),
    item(N, _, _),
    COND = variable(item_included(N)),
    ADD = operation(add, (PREV,(variable(item_weight(N)),()))),
    NEXT = operation(ite, (COND, (ADD,(PREV,())))).

% Capacity Constraint
ensure(capacity_constraint, operation(leq, (TOTAL_WEIGHT,(variable(total_capacity),())))) :- weight(_, TOTAL_WEIGHT).

% Optimization for Value
optimize_maximizeSum(dummy, EXPR, ID) :- 
    item(ID, _, _),
    COND = variable(item_included(ID)),
    EXPR = operation(if, (COND, (variable(item_value(ID)),()))).
```

If you run this encoding with the provided item data and capacity, the constraint handler will compute the optimal selection of items that maximizes the total value without exceeding the weight limit of the knapsack.

Try it yourself and come back and compare to the expected solution below!

We're looking for the items `1`, `2`, `4`, and `5` to be included in the knapsack, which gives a total weight of `0.02 + 0.15 + 2.4 + 1.8 = 4.37 kg` (within the `5.0 kg` limit) and a total value of `1200.0 + 300.0 + 1600.0 + 1100.0 = 4200.0 €`, which is the maximum possible value under the constraints.

Adding `#show value/2.` to the end of the program should give you an output similar to this:

```prolog
value(item_included(8),val(bool,false)) 
value(item_included(7),val(bool,false)) 
value(item_included(6),val(bool,false)) 
value(item_included(3),val(bool,false)) 
value(item_included(5),val(bool,true)) 
value(item_included(4),val(bool,true)) 
value(item_included(2),val(bool,true)) 
value(item_included(1),val(bool,true)) 
value(total_capacity,val(float,float("5.0"))) 
value(item_weight(1),val(float,float("0.02"))) 
value(item_weight(2),val(float,float("0.15"))) 
value(item_weight(3),val(float,float("0.8"))) 
value(item_weight(4),val(float,float("2.4"))) 
value(item_weight(5),val(float,float("1.8"))) 
value(item_weight(6),val(float,float("3.5"))) 
value(item_weight(7),val(float,float("2.0"))) 
value(item_weight(8),val(float,float("4.0"))) 
value(item_value(1),val(float,float("1200.0"))) 
value(item_value(2),val(float,float("300.0"))) 
value(item_value(3),val(float,float("850.0"))) 
value(item_value(4),val(float,float("1600.0"))) 
value(item_value(5),val(float,float("1100.0"))) 
value(item_value(6),val(float,float("1800.0"))) 
value(item_value(7),val(float,float("50.0"))) 
value(item_value(8),val(float,float("20.0")))
```