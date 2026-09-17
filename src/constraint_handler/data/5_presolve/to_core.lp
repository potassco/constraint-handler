%%%%%%%%%%%%%%%%% engines
#defined engine_request/1.
#defined engine_request/2.

#defined warning_forbid/1.
#defined warning_forbid/2.
#defined warning_ignore/1.
#defined warning_ignore/2.

ch_core(engine_request(ENG),_label_anonymous) :- engine_request(ENG), _engine(ENG).
ch_core(engine_request(ENG),LBL) :- engine_request(ENG,LBL), _engine(ENG).

%%%%%%%%%%%%%%%%% warnings
ch_core(warning_forbid(KIND),LBL) :- warning_forbid(KIND,LBL).
ch_core(warning_ignore(KIND),LBL) :- warning_ignore(KIND,LBL).

ch_core(warning_forbid(KIND),_label_anonymous) :- warning_forbid(KIND).
ch_core(warning_ignore(KIND),_label_anonymous) :- warning_ignore(KIND).
