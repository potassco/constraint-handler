"""Tests for the optional CH ground program dump."""

from io import StringIO

from clingo import Control, Function, Number

from constraint_handler import add_to_control


def test_ground_output_uses_names_for_hidden_atoms():
    ctrl = Control()
    with StringIO() as output:
        add_to_control(ctrl, ground_output=output)
        ctrl.add("{dump_hidden}. dump_shown :- not dump_hidden. #show dump_shown/0.")
        ctrl.ground()

        lines = output.getvalue().splitlines()
        assert "{dump_hidden}." in lines
        assert "dump_shown :- not dump_hidden." in lines
        assert "#show dump_shown : dump_shown." in lines
        assert ctrl.solve(assumptions=[(Function("dump_shown"), True)]).satisfiable


def test_ground_output_appends_only_new_rules_on_each_call():
    ctrl = Control()
    with StringIO() as output:
        add_to_control(ctrl, ground_output=output)
        ctrl.add("base", [], "{dump_first(X)} :- X = 1..2.")
        ctrl.add("next", ["step"], "dump_second(step,X) :- dump_first(X).")
        ctrl.ground()
        first_dump = output.getvalue()
        assert "{dump_first(1)}." in first_dump.splitlines()
        assert "dump_second" not in first_dump

        for step in (3, 4):
            previous_dump = output.getvalue()
            ctrl.ground(parts=[("next", [Number(step)])])
            new_lines = set(output.getvalue()[len(previous_dump) :].splitlines())
            assert {f"dump_second({step},{item}) :- dump_first({item})." for item in (1, 2)} <= new_lines
            assert "{dump_first(1)}." not in new_lines
            assert f"dump_second({step - 1},1) :- dump_first(1)." not in new_lines


def test_ground_output_instantiates_rules_and_show_terms():
    ctrl = Control()
    with StringIO() as output:
        add_to_control(ctrl, ground_output=output)
        ctrl.add("""
        dump_domain(1..3).
        {dump_pick(X)} :- dump_domain(X).
        dump_skip(X) :- dump_domain(X), not dump_pick(X).
        #show dump_result(X) : dump_skip(X).
        """)
        ctrl.ground()

        lines = set(output.getvalue().splitlines())
        for item in range(1, 4):
            assert f"dump_domain({item})." in lines
            assert f"{{dump_pick({item})}}." in lines
            assert f"dump_skip({item}) :- not dump_pick({item})." in lines
            assert f"#show dump_result({item}) : dump_skip({item})." in lines


def test_ground_output_replays_aggregate_and_optimization():
    original = Control()
    with StringIO() as output:
        add_to_control(original, ground_output=output)
        original.add("""
        dump_weight(1..4).
        {dump_pick(X)} :- dump_weight(X).
        :- #sum { X : dump_pick(X) } < 5.
        #minimize { X@1,X : dump_pick(X) }.
        """)
        original.ground()
        dump = output.getvalue()

    assert "#sum {" in dump
    assert "#minimize {" in dump
    replay = Control()
    replay.add(dump)
    replay.ground()

    for ctrl in (original, replay):
        costs = []
        with ctrl.solve(yield_=True) as handle:
            for model in handle:
                costs.append(tuple(model.cost))
            assert handle.get().satisfiable
        assert costs[-1] == (5,)


def test_ground_output_instantiates_externals_and_heuristics():
    ctrl = Control()
    with StringIO() as output:
        add_to_control(ctrl, ground_output=output)
        ctrl.add("""
        dump_domain(1..2).
        #external dump_enabled(X) : dump_domain(X).
        #heuristic dump_enabled(X) : dump_domain(X). [X@1,true]
        """)
        ctrl.ground()

        lines = set(output.getvalue().splitlines())
        for item in (1, 2):
            assert f"#external dump_enabled({item}). [false]" in lines
            assert f"#heuristic dump_enabled({item}). [{item}@1,true]" in lines


def test_ground_output_keeps_ch_bool_evaluated_in_rule_bodies():
    ctrl = Control(["0"])
    with StringIO() as output:
        add_to_control(ctrl, ground_output=output)
        ctrl.add("""
        dump_switch(left;right).
        variable_declare(X,boolDomain) :- dump_switch(X).
        bool_evaluate(variable(X)) :- dump_switch(X).
        dump_state(X,B) :- dump_switch(X), bool_evaluated(variable(X),val(bool,B)).
        #show dump_state/2.
        """)
        ctrl.ground()

        lines = set(output.getvalue().splitlines())
        for switch in ("left", "right"):
            for state in ("true", "false"):
                assert f"dump_state({switch},{state}) :- bool_evaluated(variable({switch}),val(bool,{state}))." in lines

        with ctrl.solve(yield_=True) as handle:
            assignments = {frozenset(map(str, model.symbols(shown=True))) for model in handle}
            assert handle.get().satisfiable
        assert assignments == {
            frozenset((f"dump_state(left,{left})", f"dump_state(right,{right})"))
            for left in ("true", "false")
            for right in ("true", "false")
        }


def test_ground_output_is_opt_in():
    ctrl = Control()
    original_ground = ctrl.ground

    add_to_control(ctrl)

    assert ctrl.ground == original_ground
