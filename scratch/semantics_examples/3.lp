%*
Language fragment:
{singleton,set,multimap}_assign(<name>,(<key>),<expression>):
    occurence: head only
    description: Assigns the value of an expression to a singleton, set, or multimap under the given variable <name> (and <key>).
{singleton,set,multimap}_choice(<name>,(<key>),<expression>):
    occurence: head only
    description: Justifies up to one value of <expression> to a singleton, set, or multimap under the given variable <name> (and <key>).
{singleton,set,multimap}_default(<name>,(<key>),<expression>,(<condition>),(<priority>)):
    occurence: head only
    description: Gives value of <expression> as default to a singleton, set, or multimap under the given variable <name> (and <key>) if the optional <condition> holds, with an optional <priority>.
default_mode({basic,assign,depends}):
    occurence: head only, domain only
    description: Specifies the default mode. Basic defaults are defeated by any justification of a different value, assign defaults only by specific variable assignments, and depends defaults by variable assignments of dependent variables.
    default: assign
ensure(<expression>):
    occurence: head only
    description: Ensures that the given expression evaluates to val(bool,true).
*%

singleton_choice(x,val(int,4)).

%*
Expected solutions:
1:
    x = val(int,4).
2:
*%