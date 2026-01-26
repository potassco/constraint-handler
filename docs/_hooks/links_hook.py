"""
This module defines a MkDocs hook that appends standardized link definitions
to the end of each Markdown page. This allows authors to use consistent link
labels throughout the documentation without manually defining them on each page.

Link labels are shortcuts for commonly referenced documents or sections. Instead
of typing out full URLs, authors can simply use the defined labels in their
Markdown content.

Example:
Given `SomeSection` at the URL `/some/path/to/some/file.md#section` we would
have to type [SomeSection](/some/path/to/some/file.md#section) whenever
this link is required.

After defining the label

"SomeSection": "/some/path/to/some/file.md#section"

we can instead simply type [SomeSection] and it will automatically resolve to the
full link at build time.

This makes it more convenient and robust to maintain links, as changes to target URLs
only need to be made in one place (the LINKS dictionary) rather than throughout the entire
documentation.
"""

import os

LINKS = {
    # User Guide
    "installation": "user_guide/installation.md",

    # Language Concepts
    "Language Concepts": "reference/language_concepts.md",
    "Valuation": "reference/language_concepts.md#valuation",
    "Expression": "reference/language_concepts.md#expression",
    "Statement": "reference/language_concepts.md#statement",
    "Fact": "reference/language_concepts.md#fact",
    "Declaration": "reference/language_concepts.md#declaration",
    "Result": "reference/language_concepts.md#result",
    # Core Syntax
    "Core Syntax": "reference/core_syntax.md",
    "List": "reference/core_syntax.md#list",
    "Value": "reference/core_syntax.md#value",
    "Val": "reference/core_syntax.md#value",
    "Variable": "reference/core_syntax.md#variable",
    "Domain": "reference/core_syntax.md#domain",
    "variable_domain": "reference/core_syntax.md#domain",
    "variable_define": "reference/core_syntax.md#define",
    "variable_declare": "reference/core_syntax.md#declare",
    "variable_declareOptional": "reference/core_syntax.md#optional",
    "Operation": "reference/core_syntax.md#operation",
    "Ensure": "reference/core_syntax.md#ensure",
    # Base Types
    "Type": "reference/base_types.md",
    "Operator Signatures": "reference/base_types.md#operator-signatures",
    "Base Type": "reference/base_types.md",
    "None": "reference/base_types.md#none",
    "Int": "reference/base_types.md#int",
    "Bool": "reference/base_types.md#bool",
    "Float": "reference/base_types.md#float",
    "String": "reference/base_types.md#string",
    "Symbol": "reference/base_types.md#symbol",
    # Collections
    "Collection": "reference/collections.md",
    "Tuple Expression": "reference/collections.md#tuple-expressions",
    "Set": "reference/collections.md#set",
    "set_declare": "reference/collections.md#declare",
    "set_assign": "reference/collections.md#assign",
    "set_value": "reference/collections.md#output_1",
    "multimap_declare": "reference/collections.md#declare_1",
    "multimap_assign": "reference/collections.md#assign_1",
    "multimap_value": "reference/collections.md#output_3",
    "Multimap": "reference/collections.md#multimap",
    # Conditionals
    "If": "reference/conditionals.md#if",
    "Ite": "reference/conditionals.md#ite",
    "Default": "reference/conditionals.md#default",
    "HasValue": "reference/conditionals.md#hasvalue",
    # Optimization
    "Optimization": "reference/optimization.md",
    "optimize_maximizeSum": "reference/optimization.md#maximize-sum",
    "optimize_precision": "reference/optimization.md#precision",
    # Engines
    "requestEngine": "reference/engines.md#request",
    "defaultEngine": "reference/engines.md#default",
    # Preference
    "preference": "reference/preference.md",
    "preference_maximizeScore": "reference/preference.md#maximize-score",
    "preference_holds": "reference/preference.md#holds",
    "preference_variableValue": "reference/preference.md#variable-value",
    "preference_score": "reference/preference.md#preference-score",

    # Execution
    "Assign Statement": "reference/execution.md#assign",
    "execution_declare": "reference/execution.md#declare",
    "execution_run": "reference/execution.md#run",
    "If Statement": "reference/execution.md#if",
    "seq2": "reference/execution.md#sequence",
    "noop": "reference/execution.md#no-operation",
    "assert": "reference/execution.md#assert",
    "while": "reference/execution.md#while",
    # Python Integration
    "statement_python": "reference/python_integration.md#statement",
    # Error Handling
    "warning": "reference/error_handling.md#warning",
}
"""
The dictionary of link labels to their corresponding target paths.

Keys are the labels used in Markdown (e.g., [Term]), and values are the
relative paths to the target files or sections within the documentation.
"""

def on_page_markdown(markdown, page, config, files):
    """
    Generates Markdown link definitions relative to the source file location.

    Technically, we could use relative paths to the /doc/ directory, which would
    require less complexity here. However, this leads to issues with mkdocs where
    paths using `.md` are not found and paths without it are unrecognized.

    The paths without `.md` would still work, but mkdocs would emit warnings for
    each occurrence, which clutters the build output and may hide real issues.

    This, we resort to calculating relative paths from the source file to ensure
    that links are correctly resolved without warnings.
    """
    definitions = ["\n\n"]
    
    current_dir = os.path.dirname(page.file.src_uri)
    
    for label, target in LINKS.items():
        if '#' in target:
            path, anchor = target.split('#', 1)
            anchor = '#' + anchor
        else:
            path = target
            anchor = ''

        rel_path = os.path.relpath(path, current_dir).replace(os.sep, '/')
        final_link = f"{rel_path}{anchor}"

        definitions.append(f"[{label}]: {final_link}")
        if not label.endswith('s'):
            definitions.append(f"[{label}s]: {final_link}")

    return markdown + "\n".join(definitions)