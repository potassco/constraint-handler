from __future__ import annotations

import graphlib
from collections import defaultdict
from typing import Any, NamedTuple

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression



def print_results(res):
    s = ""
    for a, v in res.items():
        s += f"{(str(a),str(v))}\n"
    return s


# type ReducedExpr = expression.Val | frozenset[ReducedExpr] | refe | tuple[ReducedExpr, ...]


class Value(NamedTuple):
    var: expression.constant
    val: Any


class Ref(NamedTuple):
    type_: expression.BaseType | clingo.Symbol
    expr: expression.Expr


class _set_contains(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class _se_value(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


type Result = _se_value | _set_contains


def set_map(ctrl: clingo.Control):
    res = myClorm.findInControl(ctrl, Result)
    map = dict()
    for atom, value in res.items():
        map[atom.symbol] = value
    setattr(ctrl, "constraint_handler_map", map)


def set_valuation(ctrl, model) -> dict[Any, Any]:
    ts = graphlib.TopologicalSorter()
    vals = dict()
    mems = defaultdict(set)
    map = ctrl.constraint_handler_map
    results2 = []
    # print("feb 3: vals",list(model.symbols(atoms=True,theory=True)))
    for s in model.symbols(atoms=True, theory=True):
        if s in map:
            results2.append(map[s])
    # results = myClorm.findInModel(model,Result)
    # for r in results.values():
    #    if r not in results2:
    #        print("missing from 2",r)
    # for r in results2:
    #    if r not in results.values():
    #        print("missing from 1",r)
    # assert False
    for a in results2:
        # print(a,type(a))
        # for a in results.values():
        if isinstance(a, _se_value):
            if isinstance(a.val, Ref):
                if a.val.type_ == expression.BaseType.set:
                    vals[a.expr] = set()
                elif a.val.type_ == expression.BaseType.multimap:
                    vals[a.expr] = dict()
                else:
                    print("feb 1", "unsupported", a)
                    assert False
            elif isinstance(a.val, expression.Val):
                vals[a.expr] = a.val.value
                vals[a.val] = a.val.value
                # if a.val.type_ == expression.BaseType.set:
                #    print("feb 1", "unsupported", a)
                #    assert False
                # else:
                #    vals[a.expr] = a.val.value
            elif isinstance(a.val, expression.Bad):
                vals[a.expr] = expression.Bad
            else:
                print("feb 1", "unsupported", a)
                assert False
        elif isinstance(a, _set_contains):
            if isinstance(a.val, Ref):
                if a.val.type_ == expression.BaseType.set:
                    # print("feb 3", "adding a.val.expr", a)
                    mems[a.val.expr].add(a.expr)
                    ts.add(a.expr, a.val.expr)
                # elif a.val.type_ == expression.BaseType.multimap:
                #    mems[a.val.expr].add(a.expr)
                #    ts.add(a.expr,a.val.expr)
                else:
                    print("feb 1", "unsupported", a)
                    assert False
            elif isinstance(a.val, expression.Val):
                # print("feb 16", "adding a.val", a.val, a)
                mems[a.val].add(a.expr)
                # vals[a.expr] = a.val.value
                vals[a.expr] = {a.val.value} | (vals[a.expr] if a.expr in vals else set())
                ts.add(a.expr, a.val)
            else:
                print("feb 1", "unsupported", a)
                assert False
        #            ts.add(a.expr,[get_ref(a.val)])
        # elif isinstance(a, _multimap_entry):
        else:
            print("feb1", "unsupported", a)
    acyclic = False
    try:
        ts.prepare()
        acyclic = True
    except graphlib.CycleError as exn:
        print("cycle:", exn)
    # step = 0
    # while step < 20 and ts.is_active():
    #    step += 1
    # print()
    # print("feb 3: vals",vals)
    # assert acyclic
    # while acyclic and ts.is_active():
    while ts.is_active():
        ready = ts.get_ready()
        # print(ready)
        for x in ready:
            assert x in vals, f"{x},\n\n{print_results(results)},\n\n{vals}"
            if isinstance(vals[x], set):
                vals[x] = frozenset(vals[x])
            elif isinstance(vals[x], dict):
                vals[x] = multimap.HashableDict(vals[x])
            if x in mems:
                for s in mems[x]:
                    vals[s].add(vals[x])
            ts.done(x)
    pyVals = {x.arg: v for (x, v) in vals.items() if isinstance(x, expression.Variable)}
    setattr(model, "constraint_handler_valuation", pyVals)
    # clVals = [ myClorm.pytocl(atom.Value(x,str(v))) for x,v in pyVals.items() ]
    clVals = [myClorm.pytocl(atom.Value(x, evaluator.reducedExpr(v))) for x, v in pyVals.items()]
    model.extend(clVals)
    # print("extended:",pyVals)
