from itertools import combinations, groupby
from prettytable import PrettyTable
import MyDecorators as Dec
import My


class Tree:
    """ Class used to calculate all the possible forms of arraging groups of clients in groups of Tables.
        Mainly a Tree that grows staging all the possibilities or arraging clients.

        It has two main methods:
            * build_tree(): build the tree with all the possibilities of arraging clients in tables.
            * get_branches():  get the branches of the Tree.   
        An extra method can be used to print all the branches of the tree
            * print_branches()
    """
    def __init__(self, clients, tables, timeit=False, debug=False):
        class _Node:
            """ Each Node of the Tree """
            def __init__(self, cantidades, comb_tables, tables, level):
                self.cantidades = cantidades
                self.hijos = []
                self.comb_tables = comb_tables
                self.tables = tables
                self.level = level

        def _build_tree(node):
            if not node.cantidades:
                return
            else:
                cantidades_aux = node.cantidades.copy()
                m = next(iter(cantidades_aux))  # De cuanto son las tables
                n = cantidades_aux.pop(m)  # Cuantas de esas tables necesito
                tables_de_interes = filter(lambda x: int(m) in x.capacidad, node.tables)
                for tupla in combinations(
                    tables_de_interes, n
                ):  # Iterar sobre todas las combinaciones posibles de tables
                    tables_aux = tuple(
                        filter(lambda table: table not in tupla, node.tables)
                    )
                    new_node = _Node(
                        tables=tables_aux,
                        comb_tables=tupla,
                        cantidades=cantidades_aux,
                        level=node.level + 1,
                    )
                    node.hijos.append(new_node)
                    _build_tree(node=new_node)
                return

        @Dec.debug
        @Dec.timeit
        def build_tree(node, timeit=False, debug=True):
            _build_tree(node)

        @Dec.debug
        @Dec.timeit
        def get_branches(node, timeit=False, debug=True):
            def _get_branches(node):
                if not node.hijos:
                    return [node.comb_tables]
                else:
                    branches = []
                    if node.level != 0:
                        for hijo in node.hijos:
                            branches.extend(_get_branches(hijo))
                        for i in range(len(branches)):
                            branches[i] = branches[i] + node.comb_tables
                    else:
                        for hijo in node.hijos:
                            branches.extend(_get_branches(hijo))
                    return branches

            def _gname(x):
                out = []
                for i in range(len(x)):
                    out.append(x[i].name)
                return tuple(out)

            def _fname(x):
                out = ""
                for i in range(len(x)):
                    out += x[i].name[-2:]
                return out

            branches = _get_branches(node)  # Recupero las branches del tree
            total = sum(node.cantidades.values())  # Cantidad de clientes
            branches = list(
                filter(lambda x: len(x) == total, branches)
            )  # Elimina las branches que son mas cortas
            branches = [
                sorted(branche, key=lambda table: table.name) for branche in branches
            ]  # Las ordeno por placer visual
            branches = sorted(branches, key=_fname)  # Las ordeno por placer visual
            group_obj = groupby(branches, key=_gname)  # Elimina duplicados
            branches = [list(value)[0] for key, value in group_obj]  # Elimina duplicados
            return branches

        self.tables = tables
        cantidades = {}
        for client in clients:  # Carga el dic cantidades
            try:
                cantidades[f"{client.cant}"] += 1
            except:
                cantidades[f"{client.cant}"] = 1

        node = _Node(cantidades=cantidades, comb_tables=None, tables=tables, level=0)
        build_tree(node, timeit=timeit, debug=debug)
        self.branches = get_branches(node, timeit=timeit, debug=debug)

    @Dec.debug
    @Dec.timeit
    def print_branches(self, title="", timeit=False, debug=False):
        x = PrettyTable()
        x.title = title
        field_names = ["branche"]
        for table in self.tables:
            field_names.append(f"{table.name}-{table.capacidad}")
        x.field_names = field_names
        for i, branche in enumerate(self.branches):
            row = [i]
            for table in self.tables:
                if table in branche:
                    row.append("X")
                else:
                    row.append("")
            x.add_row(row)
        print(x)
