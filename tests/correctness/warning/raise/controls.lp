warning_raise(ignored).
warning_ignore(ignored).

warning_raise(labeled,none,val(bool,true),suppressed).
warning_raise(labeled,none,val(bool,true),visible).
warning_ignore(labeled,suppressed).

variable_declare(global_flag,boolDomain).
warning_raise(forbidden,none,variable(global_flag)).
warning_forbid(forbidden).

variable_declare(labeled_flag,boolDomain).
warning_raise(filtered,none,variable(labeled_flag),blocked).
warning_raise(filtered,none,val(bool,true),allowed).
warning_forbid(filtered,blocked).

variable_declare(overridden_flag,boolDomain).
warning_raise(overridden,none,variable(overridden_flag)).
warning_ignore(overridden).
warning_forbid(overridden).
