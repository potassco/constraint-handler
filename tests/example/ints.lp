#include "includeAll.lp".

%%% x = 20     two = 2     ten = 10
%%% addtwoten = two+ten = 12     addtentwo = ten+two = 12
%%% multtwoten = two*ten = 20     multtentwo = ten*two = 20
%%% subtwoten = two-ten = -8     subtentwo = ten-two = 8
%%% divtwoten = two/ten = 0     divtentwo = ten/two = 5
%%% powtwoten = two**ten = 1024     powtentwo = ten**two = 100

%%% all:
%%% x = 20     x+10 = 30     two+ten = 12     ten+two = 12
%%% two*ten = 20     ten*two = 20     two-ten = -8     ten-two = 8
%%% addtwoten==addtentwo     not multtwoten!=multtentwo
%%% not subtwoten==subtentwo     -subtwoten==subtentwo
%%% |subtwoten| = 8     |subtentwo| = 8
%%% divtwoten = 0     divtentwo = 5     powtwoten = 1024     powtentwo  = 100
%%%  -two!=two     --two!=two     two<=ten     two<ten     not two>=ten     not two>ten
%%% addtwoten<=addtentwo     not addtwoten<addtentwo
%%% addtwoten>=addtentwo     not addtwoten>addtentwo

assign(assign_x, x, constant(int(20))).
assign(a_int, two, constant(int(2))).
assign(a_int, ten, constant(int(10))).
assign(a_int, addtwoten, operation(add,(variable(two),(variable(ten),())))).
assign(a_int, addtentwo, operation(add,(variable(ten),(variable(two),())))).
assign(a_int, multtwoten, operation(mult,(variable(two),(variable(ten),())))).
assign(a_int, multtentwo, operation(mult,(variable(ten),(variable(two),())))).
assign(a_int, subtwoten, operation(sub,(variable(two),(variable(ten),())))).
assign(a_int, subtentwo, operation(sub,(variable(ten),(variable(two),())))).

assign(a_int, divtwoten, operation(div,(variable(two),(variable(ten),())))).
assign(a_int, divtentwo, operation(div,(variable(ten),(variable(two),())))).
assign(a_int, powtwoten, operation(pow,(variable(two),(variable(ten),())))).
assign(a_int, powtentwo, operation(pow,(variable(ten),(variable(two),())))).

evaluate(add,(variable(x),(constant(int(10)),()))).
evaluate(add,(variable(two),(variable(ten),()))).
evaluate(add,(variable(ten),(variable(two),()))).
evaluate(mult,(variable(two),(variable(ten),()))).
evaluate(mult,(variable(ten),(variable(two),()))).
evaluate(sub,(variable(two),(variable(ten),()))).
evaluate(sub,(variable(ten),(variable(two),()))).
evaluate(eq,(variable(addtwoten),(variable(addtentwo),()))).
evaluate(neq,(variable(multtwoten),(variable(multtentwo),()))).
evaluate(eq,(variable(subtwoten),(variable(subtentwo),()))).
evaluate(eq,(operation(minus,(variable(subtwoten),())),(variable(subtentwo),()))).
evaluate(abs,(variable(subtwoten),())).
evaluate(abs,(variable(subtentwo),())).
evaluate(neq,(operation(minus,(variable(two),())),(variable(two),()))).
evaluate(neq,(operation(minus,(operation(minus,(variable(two),())),())),(variable(two),()))).
evaluate(leq,(variable(two),(variable(ten),()))).
evaluate(lt,(variable(two),(variable(ten),()))).
evaluate(geq,(variable(two),(variable(ten),()))).
evaluate(gt,(variable(two),(variable(ten),()))).
evaluate(leq,(variable(addtwoten),(variable(addtentwo),()))).
evaluate(lt,(variable(addtwoten),(variable(addtentwo),()))).
evaluate(geq,(variable(addtwoten),(variable(addtentwo),()))).
evaluate(gt,(variable(addtwoten),(variable(addtentwo),()))).
