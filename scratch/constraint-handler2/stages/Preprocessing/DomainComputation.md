## Description

For every expression, a domain can be either computed or approximated.
Example1: a * b Exact: Domain: [x\*y for x in dom(a) for y in dom(b)]
Approximated: Domain: [min(dom(a))\*min(dom(b)), max(dom(a))\*max(dom(b))]

Python snippets need to be computed exactly as there is no information
available for approximation.

## Algorithms

- already present in compile2 and compile3s

## TODO
