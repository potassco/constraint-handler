%%%%%%%%%%%%%%%%% conditional_hasValue/1 conditional_hasNoValue/1
conditional_hasValue(E) :- _se_value(E,V), V != val(none,none), V !=bad.
conditional_hasNoValue(E) :- direct_query(E), _se_value(E,val(none,none)).
