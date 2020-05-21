from itertools import combinations, groupby
from prettytable import PrettyTable
import MyDecorators as Dec
import My  

class Tree:
    def __init__(self,clients,mesas,timeit=False,debug=False):
        class _Node:
            """ Class for building a tree that calculates
                all possible forms of siting people in a 
                group of tables """
            def __init__(self,cantidades,comb_mesas,mesas,level):
                self.cantidades = cantidades
                self.hijos = []
                self.comb_mesas = comb_mesas
                self.mesas = mesas
                self.level = level

        def _arma_tree(node):
            if not node.cantidades:
                return
            else:
                cantidades_aux = node.cantidades.copy()           
                m = next(iter(cantidades_aux))                    # De cuanto son las mesas
                n = cantidades_aux.pop(m)                         # Cuantas de esas mesas necesito
                mesas_de_interes = filter(lambda x: int(m) in x.capacidad, node.mesas) 
                for tupla in combinations(mesas_de_interes,n):    # Iterar sobre todas las combinaciones posibles de mesas
                    mesas_aux = tuple(filter( lambda mesa: mesa not in tupla, node.mesas))
                    new_node = _Node(mesas=mesas_aux,comb_mesas=tupla,cantidades=cantidades_aux,level=node.level+1)
                    node.hijos.append(new_node)
                    _arma_tree(node=new_node)
                return
        @Dec.debug
        @Dec.timeit
        def arma_tree(node,timeit=False,debug=True):
            _arma_tree(node)

        @Dec.debug
        @Dec.timeit
        def get_ramas(node,timeit=False,debug=True):
            def _get_ramas(node):
                if not node.hijos:
                    return [node.comb_mesas]
                else:
                    ramas = []
                    if node.level != 0:
                        for hijo in node.hijos:
                            ramas.extend(_get_ramas(hijo))
                        for i in range(len(ramas)):
                            ramas[i] = ramas[i] + node.comb_mesas
                    else:
                        for hijo in node.hijos:
                            ramas.extend( _get_ramas(hijo) )     
                    return ramas
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
            ramas = _get_ramas(node)                                             # Recupero las ramas del tree
            total = sum(node.cantidades.values())                                # Cantidad de clientes
            ramas = list(filter(lambda x: len(x)==total,ramas))                  # Elimina las ramas que son mas cortas
            ramas = [ sorted(rama, key=lambda mesa:mesa.name) for rama in ramas] # Las ordeno por placer visual 
            ramas = sorted(ramas, key = _fname )                                 # Las ordeno por placer visual
            group_obj = groupby(ramas, key = _gname )                            # Elimina duplicados
            ramas = [list(value)[0] for key,value in group_obj ]                 # Elimina duplicados
            return ramas

        self.mesas = mesas
        cantidades = {}
        for client in clients: #Carga el dic cantidades
            try: 
                cantidades[f"{client.cant}"] += 1
            except:
                cantidades[f"{client.cant}"] = 1
        
        node = _Node(cantidades=cantidades,comb_mesas=None,mesas=mesas,level=0)
        arma_tree(node,timeit=timeit,debug=debug)
        self.ramas = get_ramas(node,timeit=timeit,debug=debug)

    @Dec.debug
    @Dec.timeit
    def print_ramas(self,title="",timeit=False,debug=False):
        x = PrettyTable()
        x.title = title
        field_names = ["Rama"]
        for mesa in self.mesas:
            field_names.append( f"{mesa.name}-{mesa.capacidad}" )
        x.field_names = field_names
        for i,rama in enumerate(self.ramas):
            row = [i]
            for mesa in self.mesas:
                if mesa in rama:
                    row.append("X")
                else:
                    row.append("")
            x.add_row(row)
        print(x)





