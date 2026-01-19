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

from mkdocs.utils import get_relative_url

LINKS = {
    # Language Concepts
    "Language Concepts":    "reference/language_concepts/",
    "Valuation":            "reference/language_concepts/#valuation",
    "Expressions":          "reference/language_concepts/#expression",
    "Expression":           "reference/language_concepts/#expression",
    "Statement":            "reference/language_concepts/#statement",
    "Declaration":          "reference/language_concepts/#declaration",
    "Result":               "reference/language_concepts/#result",
    
    # Core Syntax
    "Core Syntax":          "reference/core_syntax/",
    "Value":                "reference/core_syntax/#value",
    "Variable":             "reference/core_syntax/#variable",
    "Operation":            "reference/core_syntax/#operation",
    "Ensure":               "reference/core_syntax/#ensure",

    # Base Types
    "None":                 "reference/base_types/#none",
    "Int":                  "reference/base_types/#int",
    "Bool":                 "reference/base_types/#bool",
    "Float":                "reference/base_types/#float",
    "String":               "reference/base_types/#string",
    "Symbol":               "reference/base_types/#symbol",

    # Collections
    "Set":                  "reference/collections/#set",
    "Multimap":             "reference/collections/#multimap",

    # Conditionals
    "If":                   "reference/conditionals/#if",
    "Ite":                  "reference/conditionals/#ite",
    "Default":              "reference/conditionals/#default",
    "HasValue":             "reference/conditionals/#hasvalue",
}
"""
The dictionary of link labels to their corresponding target paths.

Keys are the labels used in Markdown (e.g., [Term]), and values are the
relative paths to the target files or sections within the documentation.
"""

def on_page_markdown(markdown, page, config, files):
    """
    Generates Markdown link definitions from the LINKS dictionary 
    and appends them to the bottom of every page.
    """
    
    definitions = ["\n\n"]
    
    for label, target_path in LINKS.items():
        resolved_url = get_relative_url(target_path, page.url)
        
        definitions.append(f"[{label}]: {resolved_url}")
        
    return markdown + "\n".join(definitions)