%#include "includeAll.lp".

#show suspicious/2.

expression(E) :- assign(_,X,E).
expression(E) :- ensure(_,E).
expressionList(ES) :- expression(E), E=operation(O,ES).
expression(HEAD) :- expressionList(ES), ES=(HEAD,TAIL).
expressionList(TAIL) :- expressionList(ES), ES=(HEAD,TAIL).

depend(X,Y) :- assign(_,X,E), dependExpr(E,Y).
depend(X,Y) :- depend(X,Z), depend(Z,Y).

dependExpr(E,Y) :- expression(E), E=variable(Y). %%%%

dependExpr(E,Y) :- expression(E), E=operation(O,ES), dependExpr(SUB,Y), subExprs(ES,SUB).
subExprs(ES,HEAD) :- expressionList(ES), ES=(HEAD,TAIL).
subExprs(ES,E) :- expressionList(ES), ES=(HEAD,TAIL), subExprs(TAIL,E).


defined(X) :- assign(_,X,E).
suspicious(X,Y) :- depend(X,Y), not defined(Y).

%%% DATA
assign(blinds,thickness,val(float,float("0.2"))).
assign(blinds,aa,val(int,5)).

assign(blinds,minangle, val(int,80)).
assign(blinds,maxangle, val(int,90)).
assign(blinds,minweight,val(int,21)).
assign(blinds,maxweight,val(int,24)).

multimap_declare(blinds,density).
multimap_assign(blinds,density,val(str,"alu"),val(float,float("2.7"))).
multimap_assign(blinds,density,val(str,"steel"),val(float,float("7.9"))).
multimap_assign(blinds,density,val(str,"titanium"),val(float,float("4.5"))).

%%%% CHOICES

% material in { "alu", "steel" }

assign(blinds,material,val(str,"alu")).

1 { assign(blinds,material,val(str,("alu";"steel"))) } 1.

% b,d in [3.0,3.1,...,7.0] = [30/10.0,31/10.0,...,70/10.0]
1 { assign(blinds,b,operation(div,(val(int,30..70),(val(float,float("10")),())))) } 1.
1 { assign(blinds,d,operation(div,(val(int,30..70),(val(float,float("10")),())))) } 1.

%%% CALCULATIONS

% area := (a+b)*d/2
assign(blinds,area,
    operation(div,
             (operation(mult,
                       (operation(add,
                                 (variable(a),
                                 (variable(b),()))),
                       (variable(d),()))),
             (val(int,2),())))).

% weight := area * surface density = area * thickness * density
assign(blinds,weight,
    operation(mult,
             (variable(area),
             (operation(mult,
                       (variable(thickness),
                       (operation(find,
                                 (variable(material),
                                 (variable(density),()))),()))),())))).


%               (        b-a            )    180
%alpha := arccos( --------------------- ) * ------
%               ( sqrt( (b-a)^2 + d^2 ) )     pi
assign(blinds,alpha,
    operation(python(val(str,"lambda a,b,d: math.acos((b-a)/math.sqrt((b-a)**2+d**2)) * 180 / math.pi")),
             (variable(a),
             (variable(b),
             (variable(d),()))))).

%%% CONSTRAINTS

% weight <= maxweight
% weight >= minweight
ensure(blinds,operation(leq,(variable(weight),(variable(maxweight),())))).
ensure(blinds,operation(geq,(variable(weight),(variable(minweight),())))).

% minangle <= alpha and alpha <= maxangle
ensure(blinds,
    operation(conj,
             (operation(leq,(variable(minangle),(variable(alpha),()))),
             (operation(leq,(variable(alpha),(variable(maxangle),()))),())))).

#show value/3.