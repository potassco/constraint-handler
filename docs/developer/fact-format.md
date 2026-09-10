# Fact Format

This page describes the EBNF grammar for the fact format used by the constraint handler. It describes how to build terms for types, expressions, statements, facts, and result facts.

## Basic terms

```ebnf
<type> ::=
    | "bool" | "float" | "int" | "none" | "string" | "symbol"
    | "function" | "set" | "multimap"

<term> ::= <int> | <string> | <symbol>

<terms> ::= <term> | <term> "," <terms>

<term-list> ::= "(" ")" | "(" <term> "," <term-list> ")"

<bool> ::= "true" | "false"

<int> ::= any integer literal

<string> ::= any string literal (enclosed in quotes)

<float> ::= "float" "(" <int> ")" | "float" "(" <string> ")"

<name> ::= any suitable string

<symbol> ::= <name> | <name> "(" <terms> ")"

<label> ::= <term>

<variable> ::= <term>

<variable-list> ::= "(" ")" | "(" <variable> "," <variable-list> ")"
```

## Building Expression Terms

```ebnf
<val> ::= "bad" | "val" "(" <type> "," <term> ")"

<operator> ::=
    | "python" "(" <string> ")"
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

<conditional-operator> ::= "if" | "getOrElse" | "ite" | "hasValue"

<float-operator> ::=
    | <comp-operator> | "sqrt" | "cos" | "sin" | "tan"
    | "acos" | "asin" | "atan" | "abs" | "minus"
    | "add" | "sub" | "mult" | "int_div" | "float_div" | "pow" | "floor"
    | "ceil" | "max" | "min"

<int-operator> ::=
    | <comp-operator> | "add" | "sub" | "mult"
    | "int_div" | "float_div" | "pow" | "abs" | "minus" | "max" | "min"

<multimap-operator> ::=
    | <eq-operator> | "find" | "multimap_fold" | "multimap_isin" | "multimap_make"
    | "countKeys" | "countEntries" | "sumIntEntries"
    | "maxEntries" | "minEntries"

<set-operator> ::=
    | <eq-operator> | "union" | "inter" | "diff" | "subset" | "set_make"
    | "set_isin" | "set_notin" | "cardinality" | "set_fold"

<string-operator> ::= <eq-operator> | "concat" | "length"

<lambda-expr> ::= "lambda" "(" <term-list> "," <expression> ")"

<tuple-expr> ::= "(" ")" | "(" <expressions> ")"

<expression> ::=
    | <val>
    | "variable" "(" <variable> ")"
    | "operation" "(" <operator> "," <expression-list> ")"
    | <lambda-expr>
    | "python" "(" <string> ")"
    | <tuple-expr>

<expression-list> ::= "(" ")" | "(" <expression> "," <expression-list> ")"

<expressions> ::= <expression> | <expression> "," <expressions>
```

## Building Statement Terms
```ebnf
<statement> ::=
    | "assert" "(" <expression> ")"
    | "assign" "(" <variable> "," <expression> ")"
    | "if" "(" <expression> "," <statement> "," <statement> ")"
    | "noop"
    | "statement_python" "(" <string> ")"
    | "seq2" "(" <statement> "," <statement> ")"
    | "while" "(" <int> "," <expression> "," <statement> ")"
```

## Building Facts and Declarations
```ebnf
<domain> ::= "definition" | "boolDomain" | "fromFacts" | "open" | "set" | "multimap"

<variable-atom> ::=
    | "variable_assign" "(" <variable> "," <expression> ")"
    | "variable_assign" "(" <variable> "," <expression> "," <label> ")"
    | "variable_choice" "(" <variable> "," <expression> ")"
    | "variable_choice" "(" <variable> "," <expression> "," <label> ")"
    | "variable_declare" "(" <variable> "," <domain> ")"
    | "variable_declare" "(" <variable> "," <domain> "," <label> ")"
    | "variable_default" "(" <variable> "," <expression> ")"
    | ...
    | "variable_default" "(" <variable> "," <expression> "," <expression> "," <int> "," <label> ")"
    | "variable_define" "(" <variable> "," <expression> ")"
    | "variable_define" "(" <variable> "," <expression> "," <label> ")"
    | "variable_domain" "(" <variable> "," <expression> ")"
    | "variable_domain" "(" <variable> "," <expression> "," <label> ")"

<multimap-atom> ::=
    | "multimap_assign" "(" <variable> "," <expression> "," <expression> ")"
    | "multimap_assign" "(" <variable> "," <expression> "," <expression> "," <label> ")"

<set-atom> ::=
    | "set_assign" "(" <variable> "," <expression> ")"
    | "set_assign" "(" <variable> "," <expression> "," <label> ")"
    | "set_baseDomain" "(" <variable> "," <expression> ")"
    | "set_baseDomain" "(" <variable> "," <expression> "," <label> ")"

<execution-atom> ::=
    | "execution_declare" "(" <term> "," <statement> "," <variable-list> "," <variable-list> ")"
    | "execution_declare" "(" <term> "," <statement> "," <variable-list> "," <variable-list> "," <label> ")"
    | "execution_run" "(" <term> ")"
    | "execution_run" "(" <term> "," <label> ")"

<optimize-atom> ::=
    | "optimize_maximizeSum" "(" <expression> "," <term> ")"
    | "optimize_maximizeSum" "(" <expression> "," <term> "," <expression> ")"
    | "optimize_maximizeSum" "(" <expression> "," <term> "," <expression> "," <label> ")"
    | "optimize_precision" "(" <expression> ")"
    | "optimize_precision" "(" <expression> "," <expression> ")"

<preference-atom> ::=
    | "preference_maximizeScore"
    | "preference_holds" "(" <expression> ")"
    | "preference_holds" "(" <expression> "," <int> ")"
    | "preference_holds" "(" <expression> "," <int> "," <label> ")"
    | "preference_variableValue" "(" <variable> "," <expression> ")"
    | "preference_variableValue" "(" <variable> "," <expression> "," <int> ")"
    | "preference_variableValue" "(" <variable> "," <expression> "," <int> "," <label> ")"

<warning-control-atom> ::=
    | "warning_forbid" "(" <term> ")"
    | "warning_forbid" "(" <term> "," <term> ")"
    | "warning_ignore" "(" <term> ")"
    | "warning_ignore" "(" <term> "," <term> ")"

<atom> ::=
    | "ensure" "(" <expression> ")"
    | "ensure" "(" <expression> "," <label> ")"
    | "bool_evaluate" "(" <expression> ")"
    | "bool_evaluate" "(" <expression> "," <label> ")"
    | "evaluate" "(" <expression> ")"
    | "evaluate" "(" <expression> "," <label> ")"
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
    | "value" "(" <variable> "," <val> ")"
    | "evaluated" "(" <operator> "," <expression-list>  "," <val> ")"
    | "set_value" "(" <variable> "," <val> ")"
    | "multimap_value" "(" <variable> "," <val> "," <val> ")"
    | "preference_score" "(" <int> ")"
    | "warning" "(" <warning-symbol> "," <term-list> "," <term> ")"
```
