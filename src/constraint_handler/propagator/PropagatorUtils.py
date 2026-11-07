from clingo.ast import Transformer


class ASTInspect(Transformer):
    optimality_atom_found = False

    def visit_SymbolicAtom(self, node):
        print(node)
        return node
