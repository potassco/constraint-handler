phase_request(constantFolding,false).

evaluate(ceil,(val(float,float("0.0")),())).
evaluate(floor,(val(float,float("0.0")),())).
evaluate(ceil,(val(float,float("1.5")),())).
evaluate(floor,(val(float,float("1.5")),())).
evaluate(ceil,(val(float,float("2.2")),())).
evaluate(floor,(val(float,float("2.2")),())).
evaluate(ceil,(val(float,float("-1.5")),())).
evaluate(floor,(val(float,float("-1.5")),())).
evaluate(ceil,(val(float,float("-3.9")),())).
evaluate(floor,(val(float,float("-3.9")),())).
evaluate(ceil,(val(float,float("-4.0")),())).
evaluate(floor,(val(float,float("-4.0")),())).
evaluate(ceil,(val(float,float("4.0")),())).
evaluate(floor,(val(float,float("4.0")),())).