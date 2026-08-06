_warning_forbid(KIND,INFO) :- _passed(sugar,LBL,warning_forbid(KIND,INFO)).
_warning_ignore(KIND,INFO) :- _passed(sugar,LBL,warning_ignore(KIND,INFO)).
_warning_raised(KIND,INFO) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND,INFO), not _warning_ignore(KIND,_internal(all)).
:- _warning_raised(KIND,INFO), _warning_forbid(KIND,_internal(all)).
:- _warning_raised(KIND,INFO), _warning_forbid(KIND,INFO).
warning_raised :- _warning_raised(KIND,INFO).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), _warning_raised(KIND,INFO).
