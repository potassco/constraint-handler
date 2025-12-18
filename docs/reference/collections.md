# Collections

This page documents the collection types available in the language. Because collections require variables for their elements in addition to themselves, they do not use the `assign/3` predicate used for [variables](./values_and_variables.md#variable). 

Instead, specific `declare` and `assign` predicates are provided for each collection type. Declare predicates are used to create new collections, while assign predicates are used to add elements to existing collections.

---

## Set
Sets are unordered collections of unique elements. They are useful for grouping items where order does not matter and duplicates are not allowed.

### Declaration
To declare a new set, use the `set_declare/2` predicate:

#### Input
```prolog
set_declare(Name, SetName).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `SetName` | A unique identifier of the set. |


#### Output
This, just like `assign/3` **TODO**, adds an atom of [`value/3`](../user_guide/basic_concepts.md#values) to the model. Here, the value is a reference to the set.
```prolog
value(set_name, set, ref(variable(set_name)))
```

### Assigning Elements

To add elements to a set, use the `set_assign/3` predicate:
#### Input
```prolog
set_assign(Name, SetName, Value).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `SetName` | The unique identifier of the set to which the value will be added
| `Value` | The value to be added to the set. |

#### Output
Assigning a value to a set adds an atom of `set_value/3` to the model.

```prolog
set_value(SetName, Type, Value)
```

| Name | Description |
| :--- | :--- |
| `SetName` | The unique identifier of the set. |
| `Type` | The data type of the value being added to the set.
| `Value` | The actual value being added to the set. |

!!! Example
    To create the set `my_set` and add the [ints](../base_types/#int) `1`, `3` and `5` to it, you would use the following code:

    ```prolog
    set_declare(name, my_set).
    set_assign(name, my_set, val(int, 1)).
    set_assign(name, my_set, val(int, 3)).
    set_assign(name, my_set, val(int, 5)).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_set, set, ref(variable(my_set)))
    set_value(my_set, int, val(int, 1))
    set_value(my_set, int, val(int, 3))
    set_value(my_set, int, val(int, 5))
    ```

### Make Set

The constraint handler provides a `makeSet` operator to create sets directly within expressions.

!!! Example
    To create the same set `my_set` and add the [ints](../base_types/#int) `1`, `3` and `5` to it using `makeSet`, you would use the following code:

    ```prolog
    assign(bla, my_set, operation(makeSet, (val(int, 1),(val(int, 3),(val(int, 5),()))))).
    ```

    This results in the following output atoms:

    ```prolog
    value(my_set,set,ref(makeSet((val(int,1),(val(int,3),(val(int,5),()))))))
    set_value(my_set, int, val(int, 1))
    set_value(my_set, int, val(int, 3))
    set_value(my_set, int, val(int, 5))
    ```

### Supported Operators
Once a set is created (either via declaration or returned from another operation), the following operators can be used in expressions.

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Construction** | | | | |
| `makeSet` | Make Set | N-ary | Creates a new set explicitly from a list of arguments. | [set](#set) |
| **Set Theory** | | | | |
| `union` | Union | 2 | Returns a new set containing elements from both sets (`A ∪ B`). | [set](#set) |
| `inter` | Intersection | 2 | Returns a new set containing only elements common to both sets (`A ∩ B`). | [set](#set) |
| `subset` | Subset | 2 | `true` if set `A` is a subset of set `B`. | [bool](../base_types.md#bool) |
| **Membership** | | | | |
| `isin` | Is In | 2 | `true` if element `A` is contained in set `B`. | [bool](../base_types.md#bool) |
| `notin` | Not In | 2 | `true` if element `A` is NOT contained in set `B`. | [bool](../base_types.md#bool) |
| **Analysis** | | | | |
| `length` | Cardinality | 1 | Returns the number of elements in the set. | [int](../base_types.md#int) |
| `set_fold` | Fold | 3 | Iterates over the set, applies a function to each element and accumulates the result. | **TODO** |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if two sets contain exactly the same elements. | [bool](../base_types.md#bool) |
| `neq` | Inequality | 2 | `true` if two sets differ by at least one element. | [bool](../base_types.md#bool) |

---

## Multimap
Multimaps are collections that associate keys with values. Unlike standard maps or dictionaries, where a single key is associated with a single value, multimaps associate a each key to a set of values.

### Declaration
To declare a new multimap manually, use the `multimap_declare/2` predicate.

#### Input
```prolog
multimap_declare(Name, MultimapName).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `MultimapName` | A unique identifier of the multimap. |

#### Output
This, just like `assign/3` **TODO**, adds an atom of [`value/3`](../user_guide/basic_concepts.md#values) to the model. Here, the value is the identifier of the multimap.
```prolog
value(MultimapName, multimap, MultimapName).
```

### Assigning Key-Value Pairs
To add key-value pairs to a multimap, use the `multimap_assign/4` predicate:
#### Input
```prolog
multimap_assign(Name, MultimapName, Key, Value).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `MultimapName` | The unique identifier of the multimap to which the key-value pair will be added. |
| `Key` | The key in form of a [value](./values_and_variables.md#value) to be added to the multimap. |
| `Value` | The value to be associated with the key in the multimap. |

#### Output
Assigning a key-value pair to a multimap adds an atom of `multimap_value/5` to the model.

```prolog
multimap_value(MultimapName, KeyType, KeyValue, ValueType Value)
```

| Name | Description |
| :--- | :--- |
| `MultimapName` | The unique identifier of the multimap. |
| `KeyType` | The data type of the key being added to the multimap.
| `KeyValue` | The actual key being added to the multimap. |
| `ValueType` | The data type of the value associated with the key in the multimap. |
| `Value` | The value associated with the key in the multimap. |

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
    value(my_map,multimap,my_map)
    multimap_value(my_map,int,1,str,"one")
    multimap_value(my_map,int,1,str,"uno")
    multimap_value(my_map,int,2,str,"two")
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
    value(my_map,multimap,ref(operation(multimapMake,((val(int,1),val(str,"one")),((val(int,2),val(str,"two")),((val(int,1),val(str,"uno")),())))))) 
    multimap_value(my_map,int,1,str,"one")
    multimap_value(my_map,int,1,str,"uno")
    multimap_value(my_map,int,2,str,"two")
    ```

### Supported Operators
Once a multimap is created (either via declaration or returned from another operation), the following operators
can be used in expressions.

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Construction** | | | | |
| `multimapMake` | Make Map | N-ary | Creates a new multimap from a list of `(Key, Value)` tuples. | [multimap](#multimap) |
| **Analysis** | | | | |
| `countKeys` | Count Keys | 1 | Returns the number of unique keys in the map. | [int](../base_types.md#int) |
| `countEntries` | Count Entries | 1 | Returns the total number of key-value pairs. | [int](../base_types.md#int) |
| `sumIntEntries`| Sum Entries | 1 | Sums all integer values contained in the map. | [int](../base_types.md#int) |
| `maxEntries` | Max Entry | 1 | Returns the maximum value stored in the map (by value, not key). | **TODO** |
| `minEntries` | Min Entry | 1 | Returns the minimum value stored in the map. | **TODO** |
| **Operations** | | | | |
| `find` | Find | 2 | Retrieves the value(s) associated with a specific key. | **TODO** |
| `isin` | Has Key | 2 | `true` if the specific **Key** exists in the map. | [bool](../base_types.md#bool) |
| `multimap_fold`| Fold | 3 | Iterates over every entry (Key-Value pair), applies a function to each element and accumulates the result.| **TODO** |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if two maps contain exactly the same entries. | [bool](../base_types.md#bool) |
| `neq` | Inequality | 2 | `true` if two maps differ by at least one entry. | [bool](../base_types.md#bool) |