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


### Dominik's goals / Ideas

#### Usability, Maintainability and Collaboration
- simple but expressive input language (Philipp's seems like a good start)
- clear separation between stages (preprocessing, grounding, solving, postprocessing)
- clear modularization for separate engines
- clear responsibilities/features (is the CH responsible for SSA? Does it do error correction/recovery or just error reporting?)
- simplify feature set for now (focus on clients)
- developer documentation and guidelines
- since the clear separation of stages likely means this will become a normal Clingo application: add CLI usage to use it `ch some_file.lp` or to only run certain options (only check, only preprocessing, up to ground)

#### Correctness
- clearly documented semantics for all supported features, including undefined behavior
- well structured tests for all features, including corner cases, error handling and integration tests
- larger/complex tests similar to real-world examples

#### Performance
- eventual (but not initial) support for different engines suitable for different problems (normal, propagator,...)
- performance benchmarks for different engines and problem types
- keep suite compatible with Clingo 6 for advanced profiling and easy future upgrade
- clear boundaries between ASP and Python

#### Engineering
- keep (internal) encodings flat/unnested
- interning with IDs for potential easier/performant dispatching/identification
- clear internal representations to minimize type conversions
- Clingo types only at the boundary between ASP and Python (this makes Clingo 6 integration simple)
- minimize Python calls (guarding, moving more to ASP, ...)
- minimize clingo attribute accesses (create code that makes certain assumptions possible)
- better float representation, make limits clear
- try to specialize (and use templating/ file generation if necessary) if generalization becomes performance bottleneck