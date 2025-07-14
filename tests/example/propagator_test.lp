#include "includeAll.lp".


%%% p_e1: e1 = guess true or false
%%% p_e2: e2 = guess true or false
%%% p_ec: ec = e1 & e2
%%% p_ed: ed = e1 | e2
%%% p_ee: ensure ec <-> ed

%%% there should be 2 models: { e1=true, e2=true } and { e1=false, e2=false }

1 { assign(p_e1,e1,val(bool,(true;false))) } 1.
1 { assign(p_e2,e2,val(bool,(true;false))) } 1.
assign(p_ec,ec,operation(conj,(variable(e1),(variable(e2),())))).
assign(p_ed,ed,operation(disj,(variable(e1),(variable(e2),())))).
ensure(p_ee,operation(leqv,(variable(ec),(variable(ed),())))).

%%% this refers to the new propagator engine.
%%% Because the propagator is not implemented yet, we obtain 4 models when the next line is included.
requestEngine((p_e1;p_e2;p_ec;p_ed;p_ee),propagator).

%%% This refers to the default engine.
%%% If the next line is included instead of the above, then there will be 2 models, as intended.
%requestEngine((p_e1;p_e2;p_ec;p_ed;p_ee),compile).



#show value/3.
#show usc_active/1.
#script (python)

import clingo
import constraint_handler.myClorm
import constraint_handler.evaluator

def get_ensure(prg):
    reverseMap = dict()
    for atom in prg.symbolic_atoms.by_signature("propagator_ensure",2):
        name = myClorm.cltopy(atom.symbol.arguments[0])
        expr = myClorm.cltopy(atom.symbol.arguments[1],evaluator.Expr)
        reverseMap[atom.literal] = (name,expr)
    return reverseMap

def get_assign(prg):
    reverseMap = dict()
    for atom in prg.symbolic_atoms.by_signature("propagator_assign",3):
        name = myClorm.cltopy(atom.symbol.arguments[0])
        var = myClorm.cltopy(atom.symbol.arguments[1])
        expr = myClorm.cltopy(atom.symbol.arguments[2],evaluator.Expr)
        reverseMap[atom.literal] = (name,var,expr)
    return reverseMap

def main(prg):
    prg.ground()
    ensureMap = get_ensure(prg)
    assignMap = get_assign(prg)
    ensureReadable = { key : str(val) for key,val in ensureMap.items() }
    assignReadable = { key : val for key,val in assignMap.items() }
    print("ensure",ensureReadable)
    print("assign",assignReadable)
    #for () in assignMap.items():
    mapping = {}
    for (_, var, expr) in assignMap.values():
        #print(f"The variables in {str(expr)} are {evaluator.collectVars(expr)}")
        value = evaluator.evaluate_expr(mapping,expr)
        print(f"{var} := {str(expr)} = {value}, context: {mapping}")
        mapping[var] = value
    prg.solve()

#end.
