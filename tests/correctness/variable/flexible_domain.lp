variable_declare(baa,fromFacts).
variable_domain(baa,val(bool,true)).
variable_domain(baa,val(bool,false)) :- sometimes.
variable_domain(baa,val(none,none)) :- never.
{ never } 0.
{ sometimes }.
