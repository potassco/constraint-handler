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

- clean separation between preprocessing, grounding constraints, solving,
  postprocessing
- If we have an external SSA mechanism, then static type checking would make much more sense/can be done, as every variable is only assigned once and can not change their type. So SSA on python code could then allow for type annotation and translation
- How can we provide an API that allows for having maybe python objects,
  assignments, expressions as input, and still use the ch versatile and
  transparent with regard to optimization, brave/cautious reasoning,
  incremental solving etc... Are ASP Facts a good way to represent input for
  the ch? Maybe a python representation of a "program" -> collection of
  assignments and declarations etc... is good to be able to be preprocessed,
  analyzed, annotated, etc... Finally this representation could be translated
  to ASP facts and the CH encoding

```py
input = [
   Declare("x", 5),
   Declare("y", "x"),
   Assign("z", "x*y")
]
preprocessed_input = preprocess(input)
type_annotated_input = type_annotage(preprocessed_input)
warnings = diagnose(type_annotated_innput)
...
ctl.add(problem_representation(type_annotated_input))
ctl.solve(....) whatever
```

Why `Declare` and `Assign` and maybe `Var` etc... are python objects to
describe the input of the problem, we have functions like `preprocess`,
`type_annotate`, `diagnose`, `problem_representation` that take these objects
and analyse, annotate, modify them etc... The function `problem_representation`
could transform the python objects into ASP facts, and also append the ch ASP
encoding, both things together can be used by any solver in any way. The user
should have agency about the solving process. Everything else should be hidden
inside the functions. *This is just a hypothesis, not sure if this will work*
*This would also mean that its not that easy to use an encoding to produce ch
input, but maybe a python function*

Preprocessing:

- can be ASP or python, depending on needs
- SSA
- type resolution

Encoding:

- fact based input (I would prefer all inputs to be facts as different
  optimization/preprocessing techniques are possible than with rule based
  versions)
- an analysis of why fch grounds faster, ideally with improvements for clingo6
  as a result or new modeling techniques
- only one "engine" to ease development
- reduced set of functionality, maybe a translation layer for shortcuts (only
  introduce operators that have a smaller representation that the translated
  versions (impl can be created with and and or, but maybe the direct encoding
  needs less grounding, etc...)
- non-nested sets for simplicity
- maybe a static domain based python fallback
- undefined behavior on erroneous input + warning/error
- no recovery paths from erroneous input
- to enable independent constraint handling in a propagator, static domain
  computation is needed

### Dominik's goals / Ideas

#### Usability, Maintainability and Collaboration

- simple but expressive input language (Philipp's seems like a good start)
- clear separation between stages (preprocessing, grounding, solving,
  postprocessing)
- clear modularization for separate engines
- clear responsibilities/features (is the CH responsible for SSA? Does it do
  error correction/recovery or just error reporting?)
- simplify feature set for now (focus on clients)
- developer documentation and guidelines
- since the clear separation of stages likely means this will become a normal
  Clingo application: add CLI usage to use it `ch some_file.lp` or to only run
  certain options (only check, only preprocessing, up to ground)

#### Correctness

- clearly documented semantics for all supported features, including undefined
  behavior
- well structured tests for all features, including corner cases, error
  handling and integration tests
- larger/complex tests similar to real-world examples

#### Performance

- eventual (but not initial) support for different engines suitable for
  different problems (normal, propagator,...)
- performance benchmarks for different engines and problem types
- keep suite compatible with Clingo 6 for advanced profiling and easy future
  upgrade
- clear boundaries between ASP and Python

#### Engineering

- keep (internal) encodings flat/unnested
- interning with IDs for potential easier/performant dispatching/identification
- clear internal representations to minimize type conversions
- Clingo types only at the boundary between ASP and Python (this makes Clingo 6
  integration simple)
- minimize Python calls (guarding, moving more to ASP, ...)
- minimize clingo attribute accesses (create code that makes certain
  assumptions possible)
- better float representation, make limits clear
- try to specialize (and use templating/ file generation if necessary) if
  generalization becomes performance bottleneck

### Abdallah's goals

### Conceptual

- easy to define and to identify fragments of varying levels of complexity, in
  particular for P, NP, decidable (where input size is based on the size of
  ground CH instance)
- sound and decidable static type system

### Implementation

- reasonably easy human input format
- possible extensions with feature modules (optimization, defaults, finite
  domains, ...)
- possible extensions with datatype modules with a uniform mechanism
- integration with clingo / compatibility with other tools (ie, not a
  standalone app)
- availability of additional info (types, domains, warnings, ...)
- possibility for user to express query that don't visibly change the
  statespace (ei, evaluated != value)
- practical performance tiered by features (ie, a mode/solver/engine supporting
  the core language very fast, a solver supporting a rich set of feature fairly
  fast, a proof-of-concept implementation for exotic/very experimental
  development)
- datatype modules for bool, float, int, string, symbol, set, map/dict/table,
  multimap(?), tuple, list/sequence(?), alternative float representations (like
  dyadic rationals or like current FCH),
- user-defined operators/functions
- python fallback operators/expressions
- support for user propagator
- support for iterating over collections such as sets, maps, sequences (-> some
  higher-order function support)
- dynamic type checking
- possibility to run various static analyzes without solving
- framework for developer-supplied transformations (e.g., constant folding,
  expression normalization)

### Both

- small core language
- support both kinds of generalization of brave/cautious reasoning
- possibility for user to specify post-processing in asp
- good theoretical performance of solving implementation (no unnecessary
  blow-ups)
- support for conservative partial model computation (error recovery)
- maybe statements and executions? not sure
- possibility to extend with additional theory solving, e.g. LP/MIP
- enumeration of solutions
- compatiblity/support for solving assumptions, unsat core computation,
  explanation
- compatiblity with multi-shot approaches
- support for knowledge elaboration
- static type inference (maybe partial?)
- integration in asp: dynamic variables and constraints
- bound propagation / local consistency

### Chris's goals

- add projection under brave & cautious reasoning (for performance increase of
  user testing query execution)

### Phil's goals

- clear semantic principles
  - What are our fundamental constituents?
    - singletons, sets, multimaps ect
  - What constitutes a value?
  - ASP-ish! (fits very well with CH uniqueness)
- Language guided by the principles
- Implementation guided by the principles
- Keep CH uniqueness
  - Huge variety of constructs and datatypes
  - Search space as small as possible
  - Force me to consider values
- Clean up language
  - identify core
  - naming
  - structure
  - shorten terms or linearize

## Consolidated goals & conflicts

### Consolidations (same goal, different wording)

| Theme | Contributors | Consolidated goal |
| --- | --- | --- |
| **Staged architecture** | Sven, Max, Dominik | One pipeline with explicit, decoupled, independently testable/swappable stages (preprocess -> ground -> solve -> postprocess). |
| **Input language baseline** | Sven, Dominik, Abdallah | Adopt Philipp's proposal as the input-language starting point. |
| **Small core + modular extensions** | Dominik ("simplify feature set for now"), Abdallah ("small core language" under "Both", "possible extensions with feature/datatype modules"), Phil ("identify core", "clean up language") | Minimal core language now, with optimization/brave-cautious/defaults/datatypes shipped as opt-in feature modules later. |
| **Documented/clear semantics** | Dominik ("clearly documented semantics... including undefined behavior"), Phil ("clear semantic principles", "what constitutes a value?", "fundamental constituents") | Same underlying goal: a precisely specified semantic foundation before/alongside implementation. Phil adds the concrete lens (values, singletons/sets/multimaps) Dominik's goal was missing. |
| **Explanation / query / brave-cautious reasoning** | Sven, Abdallah, Chris | Brave/cautious reasoning + assumptions/unsat-core/explanation + projection-for-performance (Chris's goal is a concrete optimization within this cluster). |
| **Type checking / SSA** | Sven, Max, Abdallah | SSA-outside-CH (Sven) enables Max's static type annotation idea, which Abdallah's static/dynamic typing goals build on. |
| **Engineering hygiene / performance internals** | Dominik, Sven ("templating technique") | Same goal at different detail levels. |
| **Search-space minimization / solving efficiency** | Abdallah ("good theoretical performance... no unnecessary blow-ups"), Phil ("search space as small as possible") | One goal: keep the ground/solving search space minimal by construction, not just fast in practice. |
| **Testing/benchmarking & Clingo 6 readiness** | Dominik | Tests/benchmarks and "keep suite compatible with Clingo 6" support the performance and correctness clusters without conflicting with anything else. |

### Direct conflicts

1. **One engine vs. multiple engines.** Max wants "only one engine to ease
   development"; Sven wants "different engines" and a propagator engine;
   Abdallah wants performance tiered across a fast core engine, a
   richer-but-slower engine, and an experimental engine. Dominik's "eventual
   (but not initial) support for different engines" is a phasing compromise:
   start with one engine, grow into multiple later.
2. **Error-handling philosophy.** Max wants "undefined behavior on erroneous
   input... no recovery paths from erroneous input" (fail-fast); Abdallah
   wants "support for conservative partial model computation (error
   recovery)". Dominik flags this exact ambiguity himself ("does it do error
   correction/recovery or just error reporting?") — needs an explicit
   decision.
3. **Standalone app vs. library/integration.** Dominik proposes a CLI
   ("`ch some_file.lp`"); Abdallah wants "integration with clingo /
   compatibility with other tools (ie, not a standalone app)". Not mutually
   exclusive (library + thin CLI wrapper), but the wording is contradictory
   as stated and should be clarified.
4. **Feature-set minimalism vs. maximalism.** This is now a three-way
   tension:
   - Minimalist: Dominik ("simplify feature set for now"), Max ("reduced set
     of functionality... non-nested sets for simplicity").
   - Maximalist: Abdallah's broad datatype/operator/propagator wishlist and
     Phil's "Keep CH uniqueness: huge variety of constructs and datatypes".
   - Phil's own goals are in tension with each other here too: "identify
     core" / "clean up language" (minimalist framing) vs. "keep CH
     uniqueness: huge variety of constructs and datatypes" (maximalist). The
     core-vs-modules resolution applies, but Phil should clarify whether
     "uniqueness" is a Phase-1 core property or a Phase-2 module set.
5. **ASP-native vs. Python-object input representation.** Phil argues input
   should stay "ASP-ish" (fits CH's fact-based uniqueness), while Max
   proposes a Python-object API layer (`Declare`/`Assign`/`Var` plus
   `preprocess`/`type_annotate` functions) sitting in front of ASP facts. Not
   strictly contradictory if Max's objects just compile down to facts, but
   Phil's principle argues for ASP semantics driving the design first,
   whereas Max explicitly questions whether facts are even the right
   representation to design around. Needs explicit reconciliation.

### Internal tension (same person)

- **Max** questions whether ASP facts are a good input representation at all
  (proposing Python objects like `Declare`/`Assign`/`Var` with
  `preprocess`/`type_annotate` functions), yet under "Encoding" states a
  preference for "fact based input... all inputs to be facts." Likely
  reconcilable as Python objects at the API layer compiled down to facts at
  the encoding layer, but should be made explicit.
- **Phil** wants to "identify core" / "clean up language" while also wanting
  to "keep CH uniqueness: huge variety of constructs and datatypes" (see
  conflict 4 above).

### Suggested phasing

- **Phase 1 (core)**: input language per Philipp's proposal, ASP-native/
  fact-based semantics (per Phil's "ASP-ish" principle), single engine,
  staged pipeline with SSA as a preprocessing step outside CH, flat/
  fact-based internal encoding, client-required features only (optimization,
  brave/cautious, defaults+priorities), fail-fast error reporting, documented
  core semantics (values, sets, multimaps — Phil + Dominik's correctness
  goal).
- **Phase 2 (extension)**: optional feature/datatype modules (Abdallah's
  wishlist + Phil's "huge variety of constructs"), multiple engines
  (propagator, tiered performance), static/dynamic type system,
  error-recovery/partial-model support, explanation/assumptions/unsat-core.

