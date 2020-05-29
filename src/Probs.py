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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

def check_time_max(nows,time_max,time_step):
    index = int((time_max.total_seconds()/60)/time_step)
    if index > len(nows):
        return nows
    else:
        return nows[:index]

def calc_probs(nows, queue, resto, time_max, timeit=False, debug=False, verbose=False, vverbose=False):
    if verbose: print("Calculating probabilities ...")
    if vverbose and queue.queue : print("    queue looks:")
    if vverbose and queue.queue : queue.print_queue()
    
    nows = check_time_max(nows,time_max,resto.time_step)

    probs = np.zeros(shape=(len(queue.queue),len(nows)))

    for i in range(len(queue.queue)):
        clients = queue.queue[0:i+1]
        if vverbose: print(f"    calculating probs for clients:")
        if vverbose: print_group(clients)
        probs[i] = calc_prob(nows,clients,resto,timeit,debug,verbose,vverbose)
    return probs

def calc_prob(nows,clients,resto,timeit=False,debug=False,verbose=False,vverbose=False):
    """ For a dermined group of clients and for all times
    """

    tree = Tree(clients,resto.tables,timeit,debug)
    if vverbose: print("    Posible ways of sitting")
    if vverbose: tree.print_branches()

    probs = np.zeros(len(nows))
    for i,now in enumerate(nows):
        p_total = 0.0
        for j,branch in enumerate(tree.branches):
            p_branch = 1.0
            for table in tree.tables_of_interest:
                if table in branch:
                    if table.status =="empty":
                        p_branch *= 1
                    else:
                        index = int(((now-table.t_in).total_seconds())/(60*resto.time_step))
                        if index >= len(resto.hists[table.hist_id]["hist_acum"]):
                            index = -1
                        p_branch *= resto.hists[table.hist_id]["hist_acum"][index]
                else:
                    if table.status=="empty":
                        p_branch *= 0.0
                    else:
                        index = int(((now-table.t_in).total_seconds())/(60*resto.time_step))
                        if index >= len(resto.hists[table.hist_id]["hist_acum"]) :
                            index = -1
                        p_branch *= (1-resto.hists[table.hist_id]["hist_acum"][index])
                        
            p_total += p_branch
        probs[i] = p_total
    #probs = np.cumsum(probs)
    return probs

def print_group(clients):
    x = PrettyTable()
    x.title = "Group"
    x.field_names = ["numb", "name", "cant", "code"]
    for i, client in enumerate(clients):
        x.add_row([i, client.name, client.cant, client.code])
    print(x)

def plot_probs(nows,probs,queue,i,resto,sits,time_max,verbose=False,save=False,show=False):
    if verbose: print("Plotting probs")
    
    nows = check_time_max(nows,time_max,resto.time_step)

    gridsize = (2, 3)
    fig = plt.figure(num=f"probs_{nows[0].strftime('%H:%M')}",figsize=(16,9),facecolor='papayawhip',edgecolor='black')
    # ------------------------------------------------------------------------------------------
    # Plot probs
    # ------------------------------------------------------------------------------------------
    ax_probs = plt.subplot2grid(gridsize, (0,0), colspan=2, rowspan=1, facecolor='antiquewhite')
    myFmt = mdates.DateFormatter('%H:%M')
    ax_probs.set_ylabel("Probability")
    ax_probs.set_xlabel("Time [H:M]")
    ax_probs.set_title(f"Probability for each client of getting sit at a determined hour. Now:{nows[0].strftime('%H:%M')}")
    ax_probs.grid(True)
    if probs.shape[0] > 0:
        for j in range(probs.shape[0]):
            ax_probs.plot(nows, probs[j,:], label = queue.queue[j].name , linewidth=3, color=queue.queue[j].color )
        ax_probs.legend(loc='best')
    else:
        ax_probs.plot(nows,np.zeros(len(nows)),linewidth=1,color='black')
    ax_probs.set_ylim(0,1)
    ax_probs.xaxis.set_major_formatter(myFmt)
    plt.setp(ax_probs.get_xticklabels(), rotation=0, ha="right", rotation_mode="anchor")
    # ------------------------------------------------------------------------------------------
    # Plot Queue Table
    # ------------------------------------------------------------------------------------------
    ax_queue = plt.subplot2grid(gridsize, (0,2), colspan=1, rowspan=1,facecolor='antiquewhite')
    cellText = []
    if probs.shape[0] > 0:
        for j,client in enumerate(queue.queue):
            cellText.append( [f"{(j+1):02d}",client.name,client.cant] )
    else:
        cellText.append( ["","",""])
    colLabels = ("Order","Name","Quantity")
    ax_queue.axis('tight')
    ax_queue.axis('off')
    ax_queue.table(cellText=cellText,colLabels=colLabels,loc='upper center',cellLoc='center')
    ax_queue.set_title('Queue status')
    # ------------------------------------------------------------------------------------------
    # Plot Resto
    # ------------------------------------------------------------------------------------------
    ax_resto = plt.subplot2grid(gridsize, (1,0), colspan=3, rowspan=1,facecolor='antiquewhite')
    #ax_resto.axis('off')
    for j,table in enumerate(resto.tables):
        x = 2.8*(j%5)
        y = 3*int(j/5) + 0.3
        if table.status=="empty":
            ax_resto.text(x=x,y=y,s=f'{table.name}:\n--:--, {table.capacity}',style='italic',bbox={'facecolor':'green','alpha':0.5})
        else:
            if table in sits:
                try: 
                    ax_resto.text(x=x,y=y,s=f'{table.name}:\n{table.t_in.strftime("%H:%M")}, {table.capacity}\n{table.client.name}', style='italic', bbox={'facecolor':'yellow','alpha':0.5})
                except:
                    ax_resto.text(x=x,y=y,s=f'{table.name}:\n{table.t_in.strftime("%H:%M")}, {table.capacity}', style='italic', bbox={'facecolor':'yellow','alpha':0.5})
            else:
                try: 
                    ax_resto.text(x=x,y=y,s=f'{table.name}:\n{table.t_in.strftime("%H:%M")}, {table.capacity}\n{table.client.name}', style='italic', bbox={'facecolor':'red','alpha':0.5})
                except:
                    ax_resto.text(x=x,y=y,s=f'{table.name}:\n{table.t_in.strftime("%H:%M")}, {table.capacity}', style='italic', bbox={'facecolor':'red','alpha':0.5})

    ax_resto.axis([-0.5, 14, -1, 8])
    ax_resto.tick_params( axis='x', which='both', bottom=False, top=False, labelbottom=False)
    ax_resto.tick_params( axis='y', which='both', left=False, right=False, labelleft=False)
    ax_resto.set_title('Resto status')

    if save: fig.savefig(fname=f"images/frame_{i:02d}")
    if show: plt.show()
    plt.close(fig)

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

        def all_combinations(tables):
            combs = []
            for i in range(len(tables)+1):
                combs.extend( list(combinations(tables,i)))
            return combs

        def _build_tree(node):
            if not node.cants:
                # When no more cants it should return all the possible combinations of tables that remain
                tuples = all_combinations(node.tables)
                for _tuple in tuples:
                    new_node = _Node(tables=None,comb_tables=_tuple,cants=None,level=node.level + 1)
                    node.children.append(new_node)
                return
            else:
                cants_aux = node.cants.copy()
                m = next(iter(cants_aux))  # De cuanto son las tables
                n = cants_aux.pop(m)  # Cuantas de esas tables necesito
                tables_of_interest = filter(lambda x: int(m) in x.capacity, node.tables)
                for tupla in combinations(tables_of_interest, n):  # Iterar sobre todas las combinaciones posibles de tables
                    tables_aux = tuple(filter(lambda table: table not in tupla, node.tables) )
                    new_node = _Node(tables=tables_aux,comb_tables=tupla,cants=cants_aux,level=node.level + 1)
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
            if branches:
                branches = tuple(filter(lambda x: x!=None, branches))
                total = sum(node.cants.values())  # Cantidad de clientes
                branches = tuple(filter(lambda x: len(x) >= total, branches))  # Elimina las branches que tienen menos mesas que la cantidad de clientes
                branches = [ sorted(branche, key=lambda table: table.name) for branche in branches] # Las ordeno por placer visual
                branches = sorted(branches, key=_fname)   # Las ordeno por placer visual
                group_obj = groupby(branches, key=_gname) # Elimina duplicados
                branches = [tuple(value)[0] for key, value in group_obj]  # Elimina duplicados
                return branches
            else:
                return []

        cants = {}
        for client in clients:  # Carga el dic cants
            try:
                cants[f"{client.cant}"] += 1
            except:
                cants[f"{client.cant}"] = 1

        def check_cond(table,cants):
            for cant in table.capacity:
                if cant in ([int(key) for key in cants.keys()]):
                    return True
            return False

        self.tables_of_interest = [ table  for table in tables if check_cond(table,cants) ]
        
        node = _Node(cants=cants, comb_tables=None, tables=self.tables_of_interest, level=0)
        build_tree(node, timeit=timeit, debug=debug)
        self.branches = get_branches(node, timeit=timeit, debug=debug)

    @Dec.debug
    @Dec.timeit
    def print_branches(self, title="", timeit=False, debug=False):
        x = PrettyTable()
        x.title = title
        field_names = ["branche"]
        for table in self.tables_of_interest:
            field_names.append(f"{table.name}-{table.capacity}")
        x.field_names = field_names
        for i, branche in enumerate(self.branches):
            row = [i]
            for table in self.tables_of_interest:
                if table in branche:
                    row.append("X")
                else:
                    row.append("")
            x.add_row(row)
        print(x)
