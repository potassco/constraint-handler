%%% unary minus checks moved from comparison
%%% -(-8)==8     -2!=2     --2==2
evaluate(eq,(operation(minus,(val(int,-8),())),(val(int,8),()))).
evaluate(neq,(operation(minus,(val(int,2),())),(val(int,2),()))).
evaluate(neq,(operation(minus,(operation(minus,(val(int,2),())),())),(val(int,2),()))).
