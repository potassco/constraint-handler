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
for [operator signatures](base_types.md#operator-signatures)

!!! Example
    The signature

    ```prolog
    ((A,B) -> B,C) -> B | C
    ```

    represents a function that takes as input a function with signature `(A,B) -> B` and a value of type `C`, and returns a value of type `B` or `C`.

---

## Set
Sets are unordered collections of unique elements. They are useful for grouping items where order does not matter and duplicates are not allowed.

### Declaration
To declare a new set, use the `set_declare/2` predicate:

#### Input
```prolog
set_declare(Identifier, Name).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | A unique identifier of the set. |


#### Output
This, just like in the case of [Variables](core_syntax.md#variable), adds an atom of `value/2` to the model. Here, the value is a reference to the set.
```prolog
value(set_name, val(set, ref(variable(set_name))))
```

### Assigning Elements

To add elements to a set, use the `set_assign/3` predicate:
#### Input
```prolog
set_assign(Identifier, Name, Value).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | The unique identifier of the set to which the value will be added
| `Value` | The value to be added to the set. |

#### Output
Assigning a value to a set adds an atom of `set_value/2` to the model.

```prolog
set_value(Name, Value)
```

| Name | Description |
| :--- | :--- |
| `Name` | The unique identifier of the set. |
| `Value` | The actual value being added to the set using the `val/2` predicate. |

!!! Example
    To create the set `my_set` and add the [ints](base_types.md/#int) `1`, `3` and `5` to it, you would use the following code:

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
    To create the same set `my_set` and add the [ints](base_types.md/#int) `1`, `3` and `5` to it using `makeSet`, you would use the following code:

    ```prolog
    assign(bla, my_set, operation(makeSet, (val(int, 1),(val(int, 3),(val(int, 5),()))))).
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
| `makeSet` | Make Set | ([list](modeling_language.md#list)[[any](base_types.md)]) $\to$ [set](#set)[[any](base_types.md)] | Creates a new set explicitly from a list of arguments. |
| **Set Theory** | | | |
| `union` | Union | ([set](#set), [set](#set)) $\to$ [set](#set) | Returns a new set containing elements from both sets. |
| `inter` | Intersection | ([set](#set), [set](#set)) $\to$ [set](#set) | Returns a new set containing only elements common to both sets. |
| `subset` | Subset | ([set](#set), [set](#set)) $\to$ [bool](base_types.md#bool) | `true` if first set is a subset of the second. |
| **Membership** | | | |
| `isin` | Is In | ([any](base_types.md), [set](#set)) $\to$ [bool](base_types.md#bool) | `true` if the element is contained in the set. |
| `notin` | Not In | ([any](base_types.md), [set](#set)) $\to$ [bool](base_types.md#bool) | `true` if the element is NOT contained in the set. |
| **Analysis** | | | |
| `length` | Cardinality | ([set](#set)) $\to$ [int](base_types.md#int) | Returns the number of elements in the set. |
| `set_fold` | Fold | ((A,B) $\to$ B, [set](#set)(A), B) $\to$ B | Iterates over the set, applies a function to each element and accumulates the result. |
| **Comparison** | | | |
| `eq` | Equality | ([set](#set), [set](#set)) $\to$ [bool](base_types.md#bool) | Returns `true` if two sets contain exactly the same elements. |
| `neq` | Inequality | ([set](#set), [set](#set)) $\to$ [bool](base_types.md#bool) | Returns `true` if two sets differ by at least one element. |

---

## Multimap
Multimaps are collections that associate keys with values. Unlike standard maps or dictionaries, where a single key is associated with a single value, multimaps associate a each key to a set of values.

### Declaration
To declare a new multimap manually, use the `multimap_declare/2` predicate.

#### Input
```prolog
multimap_declare(Identifier, Name).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | A unique identifier of the multimap. |

#### Output
This, just like in the case of [Variables](core_syntax.md#variable), adds an atom of `value/2` to the model. Here, the value is the identifier of the multimap.
```prolog
value(Name, val(multimap, Name)).
```

### Assigning Key-Value Pairs
To add key-value pairs to a multimap, use the `multimap_assign/4` predicate:
#### Input
```prolog
multimap_assign(Identifier, Name, Key, Value).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | Unique identifier of the statement. |
| `Name` | The unique identifier of the multimap to which the key-value pair will be added. |
| `Key` | The key in form of a `val/2` predicate to be added to the multimap. |
| `Value` | The value in form of a `val/2` to be associated with the key in the multimap. |

#### Output
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
Just like sets, the constraint handler provides a `multimapMake` operator to create multimaps directly within expressions.

!!! Example
    To create the same multimap `my_map` and add the key-value pairs `(1, "one")`, `(2, "two")` and `(1, "uno")` to it using `multimapMake`, you would use the following code:

    ```prolog
    assign(bla, my_map, operation(multimapMake, ((val(int, 1), val(str, "one")), ((val(int, 2), val(str, "two")), ((val(int, 1), val(str, "uno")), ()))))).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_map, val(multimap, ref(operation(multimapMake,((val(int,1),val(str,"one")),((val(int,2),val(str,"two")),((val(int,1),val(str,"uno")),()))))))) 
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
| `multimapMake` | Make Map | ([list](core_syntax.md#list)[([any](base_types.md), [any](base_types.md))]) $\to$ [multimap](#multimap) | Creates a new multimap from a list of `(Key, Value)` tuples. |
| **Analysis** | | | |
| `countKeys` | Count Keys | ([multimap](#multimap)) $\to$ [int](base_types.md#int) | Returns the number of unique keys in the map. |
| `countEntries` | Count Entries | ([multimap](#multimap)) $\to$ [int](base_types.md#int) | Returns the total number of key-value pairs. |
| `sumIntEntries`| Sum Entries | ([multimap](#multimap)) $\to$ [int](base_types.md#int) | Sums all integer values contained in the map. |
| `maxEntries` | Max Entry | ([multimap](#multimap)) $\to$ [any](base_types.md) | Returns the maximum value stored in the map (by value, not key). |
| `minEntries` | Min Entry | ([multimap](#multimap)) $\to$ [any](base_types.md) | Returns the minimum value stored in the map. |
| **Operations** | | | |
| `find` | Find | ([multimap](#multimap), [any](base_types.md)) $\to$ [list](core_syntax.md#list) | Retrieves the list of value(s) associated with a specific key. |
| `isin` | Has Key | ([any](base_types.md), [multimap](#multimap)) $\to$ [bool](base_types.md#bool) | `true` if the specific **Key** exists in the map. |
| `multimap_fold`| Fold | ([multimap](#multimap), any, any) $\to$ any | Iterates over every entry (Key-Value pair), applies a function to each element and accumulates the result.|
| **Comparison** | | | |
| `eq` | Equality | ([multimap](#multimap), [multimap](#multimap)) $\to$ [bool](base_types.md#bool) | Returns `true` if two maps contain exactly the same entries. |
| `neq` | Inequality | ([multimap](#multimap), [multimap](#multimap)) $\to$ [bool](base_types.md#bool) | Returns `true` if two maps differ by at least one entry. |