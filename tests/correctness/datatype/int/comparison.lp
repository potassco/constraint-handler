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
%%% 6//2==3   5//2==2
%%% 6/2==3.0    5/2==2.5

evaluate(eq,(val(int,12),(val(int,12),()))).
evaluate(neq,(val(int,20),(val(int,20),()))).
evaluate(eq,(val(int,-8),(val(int,8),()))).
evaluate(leq,(val(int,2),(val(int,10),()))).
evaluate(lt,(val(int,2),(val(int,10),()))).
evaluate(geq,(val(int,2),(val(int,10),()))).
evaluate(gt,(val(int,2),(val(int,10),()))).
evaluate(leq,(val(int,12),(val(int,12),()))).
evaluate(lt,(val(int,12),(val(int,12),()))).
evaluate(geq,(val(int,12),(val(int,12),()))).
evaluate(gt,(val(int,12),(val(int,12),()))).
evaluate(eq,(operation(int_div,(val(int,6),(val(int,2),()))),(val(int,3),()))).
evaluate(eq,(operation(int_div,(val(int,5),(val(int,2),()))),(val(int,2),()))).
evaluate(eq,(operation(float_div,(val(int,6),(val(int,2),()))),(val(float,float("3.0")),()))).
evaluate(eq,(operation(float_div,(val(int,5),(val(int,2),()))),(val(float,float("2.5")),()))).
evaluate(eq,(val(int,1),(val(float,float("1.0")),()))).
evaluate(neq,(val(int,1),(val(float,float("1.0")),()))).