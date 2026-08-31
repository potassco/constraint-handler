# Roadmap

## Goals

A collection of goals that we want to achieve in the next version.

### Sven's goals

- Better usability users and developers
  - Nice input language akin to Philipps proposal
  - An API as sketched in the Early grounding plan
  - Better documentation
    - Scientific paper to introduce the ch concepts
    - Description of different modules and how the connect
  - Simplify code:
    - SSA outside of CH
  
- Performance
  - Support for different engines suitable for different problems
  - Propagator engine
  - Templating technique

- Support for explanation (labels on constraints?)
- Should fulfill our client requirements.
  - Optimization
  - Brave/cautious reasoning
  - Defaults with priorities

### Max's goals (wishlist, not everything has to be fulfilled)

API:
 - clean separation between preprocessing, grounding constraints, solving, postprocessing

Preprocessing:
 - can be ASP or python, depending on needs
 - SSA
 - type resolution

Encoding:
 - fact based input (I would prefer all inputs to be facts as different optimization/preprocessing techniques are possible than with rule based versions)
 - an analysis of why fch grounds faster, ideally with improvements for clingo6 as a result or new modeling techniques
 - only one "engine" to ease development
 - reduced set of functionality, maybe a translation layer for shortcuts (only introduce operators that have a smaller representation that the translated versions (impl can be created with and and or, but maybe the direct encoding needs less grounding, etc...)
 - non-nested sets for simplicity
 - maybe a static domain based python fallback
 - undefined behavior on erroneous input + warning/error
 - no recovery paths from erroneous input
 - to enable independent constraint handling in a propagator, static domain computation is needed
