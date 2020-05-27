"""
    Probs
    =====

    Provides the classes and methods used to calculate the probabilities of a client getting sit in a determined period of time
"""
import MyDecorators as Dec
import datetime as dt
import numpy as np
from itertools import combinations, groupby
from prettytable import PrettyTable

def calc_probs(now, now_max, queue, resto, step, timeit=False, debug=False, verbose=False, vverbose=False):
    if verbose: print("Calculating probabilities ...")
    if vverbose and queue.queue : print("    queue looks:")
    if vverbose and queue.queue : queue.print_queue()
    p = np.zeros(len(queue.queue))
    for i in range(len(queue.queue)):
        clients = queue.queue[0:i+1]
        if vverbose: print(f"        calculating probs for clients:")
        if vverbose: print_group(clients)
        p[i] = calc_prob(now,now_max,step,clients,resto,timeit,debug,verbose,vverbose)

def calc_prob(now,now_max,step,clients,resto,timeit=False,debug=False,verbose=False,vverbose=False):
    """ For a dermined group of clients and for all times
    """

    tree = Tree(clients,resto.tables,timeit,debug)
    if vverbose: print("    Posible ways of sitting")
    if vverbose: tree.print_branches()

    nows = []
    while now < now_max:
        nows.append(now)
        now = now + dt.timedelta(minutes=step)
    nows = tuple(nows)

    probs = np.zeros(len(nows))
    for i,_now in enumerate(nows):
        p_total = 0.0
        for branch in tree.branches:
            p_branch = 1.0
            for table in branch:
                #                     resto.hists[hist_id][hist_acum][index]
                p_branch = p_branch * resto.hists[table.hist_id][hist_acum][int((_now-table.t_in).total_seconds/60)]
            p_total += p_branch
        probs[i] = p_total
    return probs

def print_group(clients):
    x = PrettyTable()
    x.title = "Group"
    x.field_names = ["numb", "name", "cant", "code"]
    for i, client in enumerate(clients):
        x.add_row([i, client.name, client.cant, client.code])
    print(x)

def get_starting_index(now,resto,step):
    index_vec = np.zeros(len(resto.tables),dtype=np.int8)
    for i in range(len(resto.tables)):
        if resto.tables[i].state == "empty":
            index_vec[i] = 99
        else:
            index_vec[i] = int((((now-resto.tables[i].t_in).total_seconds() )/60)/step)
    return index_vec

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
            def __init__(self, cants, comb_tables, tables, level):
                self.cants = cants
                self.children = []
                self.comb_tables = comb_tables
                self.tables = tables
                self.level = level

        def _build_tree(node):
            if not node.cants:
                return
            else:
                cants_aux = node.cants.copy()
                m = next(iter(cants_aux))  # De cuanto son las tables
                n = cants_aux.pop(m)  # Cuantas de esas tables necesito
                tables_of_interest = filter(lambda x: int(m) in x.capacity, node.tables)
                for tupla in combinations(
                    tables_of_interest, n
                ):  # Iterar sobre todas las combinaciones posibles de tables
                    tables_aux = tuple(
                        filter(lambda table: table not in tupla, node.tables)
                    )
                    new_node = _Node(
                        tables=tables_aux,
                        comb_tables=tupla,
                        cants=cants_aux,
                        level=node.level + 1,
                    )
                    node.children.append(new_node)
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
                if not node.children:
                    return [node.comb_tables]
                else:
                    branches = []
                    if node.level != 0:
                        for child in node.children:
                            branches.extend(_get_branches(child))
                        for i in range(len(branches)):
                            branches[i] = branches[i] + node.comb_tables
                    else:
                        for child in node.children:
                            branches.extend(_get_branches(child))
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
            total = sum(node.cants.values())  # Cantidad de clientes
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
        cants = {}
        for client in clients:  # Carga el dic cants
            try:
                cants[f"{client.cant}"] += 1
            except:
                cants[f"{client.cant}"] = 1

        node = _Node(cants=cants, comb_tables=None, tables=tables, level=0)
        build_tree(node, timeit=timeit, debug=debug)
        self.branches = get_branches(node, timeit=timeit, debug=debug)

    @Dec.debug
    @Dec.timeit
    def print_branches(self, title="", timeit=False, debug=False):
        x = PrettyTable()
        x.title = title
        field_names = ["branche"]
        for table in self.tables:
            field_names.append(f"{table.name}-{table.capacity}")
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
