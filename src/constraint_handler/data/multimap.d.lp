%*! multimap_declare(Label, Name)

Declares a multimap with the given name.

Args:
    - Label: The optional [Label] attached to the declaration.
    - Name: The name of the multimap.
*%

%*! multimap_declare(Name)

Shorthand for [multimap_declare/2] using an anonymous label.

Args:
    - Name: The name of the multimap.
*%

%*! multimap_assign(Label, Name, Key, Value)

Adds one key-value pair to a multimap.

Multiple values may be associated with the same key, so assignments to the same key do
not overwrite each other.

Args:
    - Label: The optional [Label] attached to the assignment.
    - Name: The name of the multimap.
    - Key: The [Expression] whose value becomes the key.
    - Value: The [Expression] whose value becomes the associated value.
*%

%*! multimap_assign(Name, Key, Value)

Shorthand for [multimap_assign/4] using an anonymous label.

Args:
    - Name: The name of the multimap.
    - Key: The [Expression] whose value becomes the key.
    - Value: The [Expression] whose value becomes the associated value.
*%

%*! multimap_value(Name, Key, Value)

One concrete key-value entry contained in a multimap.

Args:
    - Name: The name of the multimap.
    - Key: One key present in the multimap.
    - Value: One value associated with that key.
*%