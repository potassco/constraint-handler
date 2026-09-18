## Description

x = 4 + input y = x + 1 could become x = 4 + input y = 4 + input + 1

## Algorithms

## TODO

- Is this really helpful? I guess this would need to be heuristic driven? Not
  all replacements are beneficial. Create examples
- As seen in the first example, this could retrigger constant folding, maybe
  this process should be merged with constant folding
