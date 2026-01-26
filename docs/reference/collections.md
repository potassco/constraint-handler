# Collections

This page documents the collection types available in the language.

Collections follow a *declare and assign* schema. Specific declare predicates are used to create new collections, while assign predicates are used to add elements to existing collections.

---

## Notation
The following sections require an expansion on the [Notation](base_types.md#notation) introduceed for base types to include collections.

### Typed Sets
While it is currently not possible to declare typed sets directly, we will still use the notation to indicate the type of elements contained in a set. This is done to indicate that certain operators only work on sets containing specific types.

For this, we use the following notation

```prolog
set[A]
```
where `A` is a type variable representing the type of elements contained in the set.

!!! Example
    The types

    ```prolog 
    set[int]
    set[str]
    ```

    represent sets containing only integers and strings, respectively.

### Functions
If an operator takes a function as an argument, we will indicate the entire signature of the function using the same notation as 
for [Operator Signatures]

!!! Example
    The signature

    ```prolog
    ((A,B) -> B,C) -> B | C
    ```

    represents a function that takes as input a function with signature `(A,B) -> B` and a value of type `C`, and returns a value of type `B` or `C`.

---

## Tuple Expressions
The constraint handler supports tuple [Expressions] to group multiple expressions into a single unit. While these are currently not standalone collections, they are used as input for certain collection operations.

A tuple expression is created by simply enclosing multiple expressions within parentheses and separating them by commas.

The empty tuple is represented by `()`.

!!! Example
    The tuple expression

    ```prolog
    (val(symbol, color), val(symbol, red))
    ```

    groups together two symbol values: `color` and `red`.

---

## Set
Sets are unordered collections of unique elements. They are useful for grouping items where order does not matter and duplicates are not allowed.

### Declare

To declare a new set, use the `set_declare/2` predicate:

#### Input

**[Declaration]**{.badge .declaration }

```prolog
set_declare(Identifier, Name).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | A unique identifier of the set. |


#### Output

**[Result]**{.badge .result }

This, just like in the case of [Variables], adds an atom of `value/2` to the model. Here, the value is a reference to the set.
```prolog
value(set_name, val(set, ref(variable(set_name))))
```

### Assign

To add elements to a set, use the `set_assign/3` predicate:
#### Input

**[Declaration]**{.badge .declaration }

```prolog
set_assign(Identifier, Name, Value).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | The unique identifier of the set to which the value will be added
| `Value` | The value to be added to the set. |

#### Output

**[Result]**{.badge .result }

Assigning a value to a set adds an atom of `set_value/2` to the model.

```prolog
set_value(Name, Value)
```

| Name | Description |
| :--- | :--- |
| `Name` | The unique identifier of the set. |
| `Value` | The actual value being added to the set using the `val/2` predicate. |

!!! Example
    To create the set `my_set` and add the [ints] `1`, `3` and `5` to it, you would use the following code:

    ```prolog
    set_declare(name, my_set).
    set_assign(name, my_set, val(int, 1)).
    set_assign(name, my_set, val(int, 3)).
    set_assign(name, my_set, val(int, 5)).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_set, val(set, ref(variable(my_set))))
    set_value(my_set, val(int, 1))
    set_value(my_set, val(int, 3))
    set_value(my_set, val(int, 5))
    ```

### Make Set

The constraint handler provides a `makeSet` operator to create sets directly within expressions.

!!! Example
    To create the same set `my_set` and add the [ints] `1`, `3` and `5` to it using `makeSet`, you would use the following code:

    ```prolog
    variable_define(bla, my_set, operation(makeSet, (val(int, 1),(val(int, 3),(val(int, 5),()))))).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_set, val(set, ref(makeSet((val(int,1),(val(int,3),(val(int,5),())))))))
    set_value(my_set, val(int, 1))
    set_value(my_set, val(int, 3))
    set_value(my_set, val(int, 5))
    ```

### Supported Operators
Once a set is created (either via declaration or returned from another operation), the following operators can be used in expressions.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Construction** | | | |
| `makeSet` | Make Set | ([list]\[T\]) $\to$ [set]\[T\] | Creates a new set explicitly from a list of arguments. |
| **Set Theory** | | | |
| `union` | Union | ([set], [set]) $\to$ [set] | Returns a new set containing elements from both sets. |
| `inter` | Intersection | ([set], [set]) $\to$ [set] | Returns a new set containing only elements common to both sets. |
| `subset` | Subset | ([set], [set]) $\to$ [bool] | `true` if first set is a subset of the second. |
| **Membership** | | | |
| `isin` | Is In | (T, [set]\[T\]) $\to$ [bool] | `true` if the element is contained in the set. |
| `notin` | Not In | (T, [set]\[T\]) $\to$ [bool] | `true` if the element is NOT contained in the set. |
| **Analysis** | | | |
| `length` | Cardinality | ([set]) $\to$ [int] | Returns the number of elements in the set. |
| `set_fold` | Fold | ((A,B) $\to$ B, [set]\([A]\), B) $\to$ B | Iterates over the set, applies a function to each element and accumulates the result. |
| **Comparison** | | | |
| `eq` | Equality | ([set] \| [none], [set] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. Two sets have the same value if they contain the same values. |
| `neq` | Inequality | ([set] \| [none], [set] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |


!!! Example "Example: Set Fold"
    Here, we will elaborate on the `set_fold` operator with a concrete example, since it is a bit more complex than the other operators.

    The operator requires three arguments:

    1. A function with signature `(A,B) -> B` that takes an element of the set and an accumulator of type `B`, and returns a new accumulator of type `B`.
    2. A set of elements of type `A` to iterate over.
    3. An initial value for the accumulator of type `B`.

    The fold operator will then iterate over each element in the set, applying the function to the current element and the accumulator, updating the accumulator with the result. After all elements have been processed, the final value of the accumulator is returned.

    In this example, we will sum all integers in a set. For this, we assume that `val(function, add)` is a predefined function that adds two integers.

    Given is the following set:
    ```prolog
    set_declare(example, my_set).
    set_assign(example, my_set, val(int, 1)).
    set_assign(example, my_set, val(int, 2)).
    set_assign(example, my_set, val(int, 3)).
    set_assign(example, my_set, val(int, 4)).
    set_assign(example, my_set, val(int, 5)).
    ```
    or for short:
    ```prolog
    set_declare(example, my_set).
    set_assign(example, my_set, val(int, 1..5)).
    ```

    This defines the set `my_set` containing the integers from `1` to `5`.

    In order to now sum all integers in this set, we can use the `set_fold` operator as follows:

    ```prolog
    variable_define(example, set_result, FOLD) :-
        FUNC = val(function,add),
        SET = variable(my_set),
        INIT = val(int, 0),
        FOLD = operation(set_fold, (FUNC,(SET,(INIT,())))).
    ```

    - We define `FUNC` as the addition function.
    - We define `SET` as a reference to our set `my_set`.
    - We define `INIT` as the initial accumulator value `0`.
    - Finally, we construct the `set_fold` operation using these three components.

    Running this code will yield:
    ```prolog
    value(set_result,val(int,15))
    ```

    Which is the expected sum of all integers from `1` to `5`.
---

## Multimap
Multimaps are collections that associate keys with values. Unlike standard maps or dictionaries, where a single key is associated with a single value, multimaps associate a each key to a set of values.

### Declare

To declare a new multimap manually, use the `multimap_declare/2` predicate.

#### Input

**[Declaration]**{.badge .declaration }

```prolog
multimap_declare(Identifier, Name).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | A unique identifier of the multimap. |

#### Output

**[Result]**{.badge .result }

This, just like in the case of [Variables], adds an atom of `value/2` to the model. Here, the value is the identifier of the multimap.
```prolog
value(Name, val(multimap, Name)).
```

### Assign

To add key-value pairs to a multimap, use the `multimap_assign/4` predicate:
#### Input

**[Declaration]**{.badge .declaration }

```prolog
multimap_assign(Identifier, Name, Key, Value).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | The unique identifier of the multimap to which the key-value pair will be added. |
| `Key` | The key in form of a `val/2` predicate to be added to the multimap. |
| `Value` | The value in form of a `val/2` to be associated with the key in the multimap. |

!!! Note
    While we use Key-Value terminology, it is important to remember that in a multimap, each key can be associated with multiple values. Meaning, if we assign the same key multiple times with different values, all those values will be stored in a set associated with that key.

#### Output

**[Result]**{.badge .result }

Assigning a key-value pair to a multimap adds an atom of `multimap_value/5` to the model.

```prolog
multimap_value(Name, Key, Value)
```

| Name | Description |
| :--- | :--- |
| `Name` | The unique identifier of the multimap. |
| `Key` | The key in form of a `val/2` predicate being added to the multimap. |
| `Value` | The value in form of a `val/2` associated with the key in the multimap. |

!!! Example
    To create the multimap `my_map` and add the key-value pairs `(1, "one")`, `(2, "two")` and `(1, "uno")` to it, you would use the following code:

    ```prolog
    multimap_declare(name, my_map).
    multimap_assign(name, my_map, val(int, 1), val(str, "one")).
    multimap_assign(name, my_map, val(int, 2), val(str, "two")).
    multimap_assign(name, my_map, val(int, 1), val(str, "uno")).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_map,val(multimap,my_map))
    multimap_value(my_map, val(int,1), val(str,"one"))
    multimap_value(my_map, val(int,1), val(str,"uno"))
    multimap_value(my_map, val(int,2), val(str,"two"))
    ```

### Make Multimap
Just like for sets, the constraint handler provides a `multimap_make` operator to create multimaps directly within expressions. Here, all key-value pairs are provided as a list of [Tuple Expressions].

!!! Example
    To create the same multimap `my_map` and add the key-value pairs `(1, "one")`, `(2, "two")` and `(1, "uno")` to it using `multimap_make`, you would use the following code:

    ```prolog
    assign(bla, my_map, operation(multimap_make, ((val(int, 1), val(str, "one")), ((val(int, 2), val(str, "two")), ((val(int, 1), val(str, "uno")), ()))))).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_map, val(multimap, ref(operation(multimap_make,((val(int,1),val(str,"one")),((val(int,2),val(str,"two")),((val(int,1),val(str,"uno")),()))))))) 
    multimap_value(my_map,val(int,1),val(str,"one"))
    multimap_value(my_map,val(int,1),val(str,"uno"))
    multimap_value(my_map,val(int,2),val(str,"two"))
    ```

### Supported Operators
Once a multimap is created (either via declaration or returned from another operation), the following operators
can be used in expressions.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Construction** | | | |
| `multimap_make` | Make Map | ([list]\[(K, V)\]) $\to$ [multimap]\[K, V\] | Creates a new multimap from a list of `(Key, Value)` tuples. |
| **Analysis** | | | |
| `countKeys` | Count Keys | ([multimap]) $\to$ [int] | Returns the number of unique keys in the map. |
| `countEntries` | Count Entries | ([multimap]) $\to$ [int] | Returns the total number of key-value pairs. |
| `sumIntEntries`| Sum Entries | ([multimap]) $\to$ [int] | Sums all integer values contained in the map. |
| `maxEntries` | Max Entry | ([multimap]\[K, V\]) $\to$ V | Returns the maximum value stored in the map (by value, not key). |
| `minEntries` | Min Entry | ([multimap]\[K, V\]) $\to$ V | Returns the minimum value stored in the map. |
| **Operations** | | | |
| `find` | Find | ([multimap]\[K, V\], K) $\to$ [list]\[V\] | Retrieves the list of value(s) associated with a specific key. |
| `isin` | Has Key | (K, [multimap]\[K, V\]) $\to$ [bool] | `true` if the specific **Key** exists in the map. |
| `multimap_fold`| Fold | ((V,B) $\to$ B, [multimap]\[K, V\], B) $\to$ B | Iterates over all entries in the multimap, applies a function to each value and accumulates the result. |
| **Comparison** | | | |
| `eq` | Equality | ([multimap] \| [none], [multimap] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. Two multimaps have the same value if they contain the same key-value-pairs. |
| `neq` | Inequality | ([multimap] \| [none], [multimap] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |

!!! Example "Multimap Fold"
    Just like for sets, we will elaborate on the `multimap_fold` operator with a concrete example.

    The operator requires three arguments:

    1. A function with signature `(A,B) -> B` that takes an entry of the multimap and an accumulator of type `B`, and returns a new accumulator of type `B`.
    2. A multimap of entries of type `(K,V)` to iterate over.
    3. An initial value for the accumulator of type `B`.

    The fold operator will then iterate over each entry in the multimap, applying the function to the current entry and the accumulator, updating the accumulator with the result. After all entries have been processed, the final value of the accumulator is returned.

    Because all values in a multimap are stored in sets, the `multimap_fold` operator can be seen as a combination of `find` and `set_fold`. First, `find` retrieves all values associated with each key, and then `set_fold` is applied to these values.

    In this example, we will sum all integer values in a multimap. For this, we assume that `val(function, add)` is a predefined function that adds two integers.

    Given is the following multimap:
    ```prolog
    multimap_declare(example, my_map).
    multimap_assign(example, my_map, val(symbol, some_key), val(int, 1..5)).
    ```

    This defines the multimap `my_map` containing the key `some_key` associated with the integers from `1` to `5`.

    In order to now sum all integers in this multimap, we can use the `multimap_fold` operator as follows:

    ```prolog
    variable_define(example, map_result, FOLD) :-
        FUNC = val(function, add),
        MAP = variable(my_map),
        INIT = val(int, 0),
        FOLD = operation(multimap_fold, (FUNC,(MAP,(INIT,())))).
    ```

    - We define `FUNC` as the addition function.
    - We define `MAP` as a reference to our multimap `my_map`.
    - We define `INIT` as the initial accumulator value `0`.
    - Finally, we construct the `multimap_fold` operation using these three components.

    Running this code will yield:
    ```prolog
    value(map_result,val(int,15))
    ```

    Which is the expected sum of all integers from `1` to `5`.

    ---

    Given that the `multimap_fold` operator iterates over every entry in the multimap, the same function also works with multiple keys.

    For example, given the following multimap:
    ```prolog
    multimap_declare(example, my_map).
    multimap_assign(example, my_map, val(symbol, key1), val(int, 1..3)).
    multimap_assign(example, my_map, val(symbol, key2), val(int, 4..5)).
    ```

    This defines the multimap `my_map` containing the key `key1` associated with the integers from `1` to `3` and the key `key2` associated with the integers from `4` to `5`.

    Using the same `multimap_fold` code as above will now yield:
    ```prolog
    value(map_result,val(int,15))
    ```

    Which is exactly the same result as before, the expected sum of all integers from `1` to `5`.
