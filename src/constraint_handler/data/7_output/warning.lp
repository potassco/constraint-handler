#defined warning_forbid/1.
#defined warning_forbid/2.
#defined warning_ignore/1.
#defined warning_ignore/2.

_warning_forbid(KIND,LBL) :- warning_forbid(KIND,LBL).
_warning_ignore(KIND,LBL) :- warning_ignore(KIND,LBL).
_warning_forbid(KIND,_label_anonymous) :- warning_forbid(KIND).
_warning_ignore(KIND,_label_anonymous) :- warning_ignore(KIND).

_warning_raised(KIND,INFO) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND,INFO), not _warning_ignore(KIND,_label_anonymous).
:- _warning_raised(KIND,INFO), _warning_forbid(KIND,_label_anonymous).
:- _warning_raised(KIND,INFO), _warning_forbid(KIND,INFO).
warning_raised :- _warning_raised(KIND,INFO).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), _warning_raised(KIND,INFO).
