from itertools import chain, combinations

import clingo


class PowersetExplorer:
    def __init__(self, assumptions):
        self.powerset = chain.from_iterable(combinations(assumptions, r) for r in reversed(range(len(assumptions) + 1)))
        self.found_sat = []
        self.found_mucs = []

    def add_sat(self, assumptions):
        self.found_sat.append(set(assumptions))

    def add_unsat(self, assumptions):
        self.found_mucs.append(set(assumptions))

    def explored(self, assumptions):
        # skip if an already found satisfiable subset is superset
        if any(set(sat).issuperset(assumptions) for sat in self.found_sat):
            return True
        # skip if an already found muc is a subset
        if any(set(muc).issubset(assumptions) for muc in self.found_mucs):
            return True
        return False

    def get_query(self):
        while True:
            try:
                current_subset = set(next(self.powerset))
            except StopIteration:
                return None
            if len(current_subset) == 0:
                continue
            if self.explored(current_subset):
                continue
            return current_subset


class AspExplorer:
    def __init__(self, assumptions):
        self.ctrl = clingo.Control(["--heuristic=Domain"])
        self.assumption_map = dict()
        self.symbol_map = dict()
        with self.ctrl.backend() as backend:
            for a in assumptions:
                symb = clingo.Function("a", [clingo.Number(a)])
                atom = backend.add_atom(symb)
                self.assumption_map[a] = atom
                self.symbol_map[symb] = a
                backend.add_heuristic(atom, clingo.backend.HeuristicType.True_, 1, 1, [])
                backend.add_rule([atom], choice=True)

    def add_sat(self, assumptions):
        with self.ctrl.backend() as backend:
            backend.add_rule([], [-a for assumption, a in self.assumption_map.items() if assumption not in assumptions])

    def add_unsat(self, assumptions):
        with self.ctrl.backend() as backend:
            backend.add_rule([], [self.assumption_map[a] for a in assumptions])

    def explored(self, assumptions):
        literals = [a if assumption in assumptions else -a for assumption, a in self.assumption_map.items()]
        result = self.ctrl.solve(assumptions=literals)
        return not result.satisfiable

    def get_query(self):
        with self.ctrl.solve(yield_=True) as handle:
            for m in handle:
                pass
            if handle.get().satisfiable:
                atoms = handle.last().symbols(atoms=True)
                return [self.symbol_map[atom] for atom in atoms]
            else:
                return None


def minimizeCore(prg, e, literals):
    with prg.solve(assumptions=literals, yield_=True) as handle:
        for m in handle:
            pass
        if handle.get().satisfiable:
            e.add_sat(tuple(literals))
            return None
        else:
            maybe = [a for a in literals if a in handle.core()]
    include = []
    while maybe:
        a = maybe.pop()
        ass = tuple(maybe + include)
        if e.explored(ass):
            include.append(a)
            continue
        with prg.solve(assumptions=ass, yield_=True) as handle:
            for m in handle:
                pass
            if handle.get().satisfiable:
                e.add_sat(ass)
                include.append(a)
            else:
                maybe = [a for a in maybe if a in handle.core()]
    return include


def enumerate_mus(prg, switchOn):
    e = AspExplorer(switchOn)
    # e = PowersetExplorer(switchOn)
    query = e.get_query()
    while query is not None:
        core = minimizeCore(prg, e, query)
        if core is not None:
            yield core
            e.add_unsat(core)
        query = e.get_query()


def get_assumptions(prg, predicate="usc_active"):
    reverseMap = dict()
    for atom in prg.symbolic_atoms.by_signature(predicate, 1):
        reverseMap[atom.literal] = atom.symbol.arguments[0]
    return reverseMap


def relax(prg, names, predicate="usc_relax"):
    for n in names:
        symb = clingo.Function(predicate, [n])
        prg.assign_external(symb, True)
