# Fact Format

This page describes the EBNF grammar for the fact format used by the constraint handler. It describes how to build terms for types, expressions, statements, facts, and result facts.

## Basic terms

```ebnf
<type> ::=
    | "bool" | "float" | "int" | "none" | "string" | "symbol"
    | "function" | "set" | "multimap"

<bool> ::= "true" | "false"

<int> ::= any integer literal

<str> ::= any string literal (enclosed in quotes)

<name> ::= any suitable string

<term> ::= <int> | <str> | <symbol>

<terms> ::= <term> | <term> "," <terms>

<symbol> ::= <name> | <name> "(" <terms> ")"

<term-list> ::= "(" ")" | "(" <term> "," <term-list> ")"
```

## Building Expression Terms

```ebnf
<val> ::= "bad" | "val" "(" <type> "," <term> ")"

<operator> ::=
    | "python" "(" <str> ")"
    | <lambda-expr>
    | <variable>
    | <bool-operator>
    | <conditional-operator>
    | <float-operator>
    | <int-operator>
    | <multimap-operator>
    | <set-operator>
    | <string-operator>

<eq-operator> ::= "eq" | "neq"

<comp-operator> ::= <eq-operator> | "leq" | "lt" | "geq" | "gt"

<bool-operator> ::=
    | <eq-operator> | "conj" | "disj" | "leqv"
    | "limp" | "lnot" | "lxor" | "snot" | "wnot"

<conditional-operator> ::= "if" | "default" | "ite" | "hasValue"

<float-operator> ::=
    | <comp-operator> | "sqrt" | "cos" | "sin" | "tan"
    | "acos" | "asin" | "atan" | "abs" | "minus"
    | "add" | "sub" | "mult" | "int_div" | "float_div" | "pow" | "floor"
    | "ceil" | "max" | "min"

<int-operator> ::=
    | <comp-operator> | "add" | "sub" | "mult"
    | "int_div" | "float_div" | "pow" | "abs" | "minus" | "max" | "min"

<multimap-operator> ::=
    | <eq-operator> | "find" | "multimap_fold" | "isin" | "multimap_make"
    | "countKeys" | "countEntries" | "sumIntEntries"
    | "maxEntries" | "minEntries"

<set-operator> ::=
    | <eq-operator> | "union" | "inter" | "diff" | "subset" | "set_make"
    | "isin" | "notin" | "length" | "set_fold"

<string-operator> ::= <eq-operator> | "concat" | "length"

<lambda-expr> ::= "lambda" "(" <term-list> "," <expression> ")"

<tuple-expr> ::= "(" ")" | "(" <expressions> ")"

<expression> ::=
    | <val>
    | "variable" "(" <term> ")"
    | "operation" "(" <operator> "," <expression-list> ")"
    | <lambda-expr>
    | <tuple-expr>

<expression-list> ::= "(" ")" | "(" <expression> "," <expression-list> ")"

<expressions> ::= <expression> | <expression> "," <expressions>
```

## Building Statement Terms
```ebnf
<statement> ::=
    | "assert" "(" <expression> ")"
    | "assign" "(" <term> "," <expression> ")"
    | "if" "(" <expression> "," <statement> "," <statement> ")"
    | "noop"
    | "statement_python" "(" <str> ")"
    | "seq2" "(" <statement> "," <statement> ")"
    | "while" "(" <int> "," <expression> "," <statement> ")"
```

## Building Facts and Declarations
```ebnf
<domain> ::= "boolDomain" | "fromFacts" | "fromList" "(" <expression-list> ")"

<variable-atom> ::=
    | "variable_declare" "(" <term> "," <domain> ")"
    | "variable_declare" "(" <term> "," <term> "," <domain> ")"
    | "variable_declareOptional" "(" <term> ")"
    | "variable_define" "(" <term> "," <expression> ")"
    | "variable_define" "(" <term> "," <term> "," <expression> ")"
    | "variable_domain" "(" <term> "," <expression> ")"

<multimap-atom> ::=
    | "multimap_declare" "(" <term> ")"
    | "multimap_declare" "(" <term> "," <term> ")"
    | "multimap_assign" "(" <term> "," <expression> "," <expression> ")"
    | "multimap_assign" "(" <term> "," <term> "," <expression> "," <expression> ")"

<set-atom> ::=
    | "set_declare" "(" <term> ")"
    | "set_declare" "(" <term> "," <term> ")"
    | "set_assign" "(" <term> "," <expression> ")"
    | "set_assign" "(" <term> "," <term> "," <expression> ")"
    | "set_baseDomain" "(" <term> "," <expression> ")"
    | "set_baseDomain" "(" <term> "," <term> "," <expression> ")"

<execution-atom> ::=
    | "execution_declare" "(" <term> "," <statement> "," <term-list> "," <term-list> ")"
    | "execution_declare" "(" <term> "," <term> "," <statement> "," <term-list> "," <term-list> ")"
    | "execution_run" "(" <term> ")"
    | "execution_run" "(" <term> "," <term> ")"

<optimize-atom> ::=
    | "optimize_maximizeSum" "(" <expression> "," <term> ")"
    | "optimize_maximizeSum" "(" <expression> "," <term> "," <expression> ")"
    | "optimize_maximizeSum" "(" <term> "," <expression> "," <term> "," <expression> ")"
    | "optimize_precision" "(" <expression> ")"
    | "optimize_precision" "(" <expression> "," <expression> ")"

<preference-atom> ::=
    | "preference_maximizeScore"
    | "preference_holds" "(" <expression> ")"
    | "preference_holds" "(" <expression> "," <int> ")"
    | "preference_holds" "(" <term> "," <expression> "," <int> ")"
    | "preference_variableValue" "(" <term> "," <expression> ")"
    | "preference_variableValue" "(" <term> "," <expression> "," <int> ")"
    | "preference_variableValue" "(" <term> "," <term> "," <expression> "," <int> ")"

<warning-control-atom> ::=
    | "ignore_warning" "(" <term> ")"
    | "forbid_warning" "(" <term> ")"
    | "forbid_warning" "(" <term> "," <term> ")"

<atom> ::=
    | "assign" "(" <term> "," <expression> ")"
    | "assign" "(" <term> "," <term> "," <expression> ")"
    | "ensure" "(" <expression> ")"
    | "ensure" "(" <term> "," <expression> ")"
    | "evaluate" "(" <operator> "," <expression-list> ")"
    | "evaluate" "(" <term> "," <operator> "," <expression-list> ")"
    | <variable-atom>
    | <multimap-atom>
    | <set-atom>
    | <execution-atom>
    | <optimize-atom>
    | <preference-atom>
    | <warning-control-atom>
```
## Result Facts
```ebnf

<expression-warning> ::=
    | "notImplemented"
    | "pythonError"
    | "syntaxError"
    | "zeroDivisionError"

<preference-warning> ::=
    | "unsupported"

<statement-warning> ::=
    | "evaluatorError"
    | "notImplemented"
    | "pythonError"

<type-warning> ::=
    | "failed_operation"

<variable-warning> ::=
    | "badValue"
    | "emptyDomain"
    | "multipleDeclarations"
    | "multipleDefinitions"
    | "undeclared"
    | "confusingName"

<warning-symbol> ::=
    | "expression" "(" <expression-warning> ")"
    | "otherError"
    | "preference" "(" <preference-warning> ")"
    | "propagator"
    | "statement" "(" <statement-warning> ")"
    | "type" "(" <type-warning> ")"
    | "variable" "(" <variable-warning> ")"

<atom> ::=
    | "value" "(" <term> "," <val> ")"
    | "evaluated" "(" <operator> "," <expression-list>  "," <val> ")"
    | "set_value" "(" <term> "," <val> ")"
    | "multimap_value" "(" <term> "," <val> "," <val> ")"
    | "preference_score" "(" <int> ")"
    | "warning" "(" <warning-symbol> "," <term-list> "," <term> ")"
```
