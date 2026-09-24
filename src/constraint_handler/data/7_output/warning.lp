_warning_forbid(KIND,LBL) :- ch_core(warning_forbid(KIND),LBL).
_warning_ignore(KIND,LBL) :- ch_core(warning_ignore(KIND),LBL).

_warning_raised(KIND,INFO) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND,INFO), not _warning_ignore(KIND,_label_anonymous).
:- _warning_raised(KIND,INFO), _warning_forbid(KIND,_label_anonymous).
:- _warning_raised(KIND,INFO), _warning_forbid(KIND,INFO).
warning_raised :- _warning_raised(KIND,INFO).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), _warning_raised(KIND,INFO).
