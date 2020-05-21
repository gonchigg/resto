"""
    My
    =====

    Provides
        1. Classes `Cola` and `Resto` to handle each.
        2. Sub-classes `Mesa` and `Client` to handle each.
        3. Functions as `load_resto()`, `load_cola()` to load data from .jsons.
        4. Functions as `giveme_llegadas()`, `giveme_levantadas` to hablde both events."""

import numpy as np
import datetime as dt
import json
import random
import Auxiliar as Aux
from prettytable import PrettyTable 

"""
    Que hace

    Parameters
    ----------
    a : Que es, optional-non-optional
        Para qur sirve

    Returns
    -------
    m : Que es
        Para que sirve

    Notes
    -----
    Lo que vos quieras

    Examples
    --------
    >>> a = np.array([[1, 2], [3, 4]])
    >>> np.mean(a)
    2.5
    >>> np.mean(a, axis=0)"""

# ------------------------------------------------------------------------------
# Sub-classes: Mesa, Client.
# ------------------------------------------------------------------------------
class Mesa:
    """ Class used to simulate and handle all the data relationed to each Table.
        Parameters
        ----------
        name: string, non-optional.
            Unique identity of each Table.
        capacidad: list of ints, non-optional.
            Amount of Clients thath can sit in each table.
        t_in: datetime.datetime object, non-optional.
            Time in which the Table was last ocuppied.
        hist_id: string, non-optional.
            Identification of the histogram that represents the behaving of the Table.
        state: string, non-optional.
            State of the Table belonging to the variable 'states'.
        client: Client object, non-optional.
            Object of the client that is currently on the Table."""
    states = ("ocupada","vacia","inactiva") # All possiblle states of a Table
    def __init__(self, name, capacidad, t_in, hist_id, state="vacia", client=None):
        """Initialize the Class Table:"""
        self.name = name
        self.client = client
        self.capacidad = capacidad
        self.t_in = t_in
        if state not in self.states:
            raise ValueError("%s is not a valid title." % state)
        self.state = state
        self.hist_id = hist_id
class Client:
    """ Class used to simulate and handle all the data relationed to each Client.
        Parameters
        ----------
        name: string, non-optional.
            Unique identity of each client.
        cant: int, non-optional.
            Amount of people willing to be located.
        code: int, non-optional.
            Unique code to identify the client.
        t_llegada: datetime.datetime object, non-optional.
            Time at which the client put himself on the Cola"""
    def __init__(self, name, code, cant, t_llegada=None):
        """Initialize the Class Client:"""
        self.name = name
        self.code = code
        self.cant = cant
        self.t_llegada = t_llegada
# ------------------------------------------------------------------------------
# Main-Classes: Cola, Resto
#       Cola ~ List of Clients, and methods
#       Resto ~ List of Mesas, and methods
# ------------------------------------------------------------------------------
class Cola:
    def __init__(self):
        self.cola = []
        self.registro_de_llegadas = None

    def add_client(self,cant,name="",t_llegada=dt.datetime.today()):
        codes = list(filter(lambda client: client.code,self.cola))
        code  = np.random.randint(low=0,high=9999)
        while code in codes:
                code = np.random.randint(low=0,high=9999)
        if name=="":
            name = f"Juan_{code:04d}"
        client = Client(name=name,code=code,cant=cant,t_llegada=t_llegada)
        self.cola.append(client)
        return client

    def actualizar_llegadas(self,now,verbose=False):
        if verbose: print(f"Actualizando llegadas")
        if self.registro_de_llegadas != [] :
            if self.registro_de_llegadas[0][0] < now:
                cond = True
            else:
                cond = False
        else:
            cond = False
        llegadas = []
        while cond: 
            llegada = self.registro_de_llegadas.pop(0)
            if verbose: print(f"    llegó cliente a las:{llegada[0].strftime('%H:%M:%S')}, son:{llegada[1]}")
            client = self.add_client(cant=llegada[1],t_llegada=llegada[0])
            llegadas.append(client)
            if self.registro_de_llegadas != [] :
                if self.registro_de_llegadas[0][0] < now:
                    cond = True
                else:
                    cond = False
            else:
                cond = False
        
    def print_cola(self):
        x = PrettyTable()
        x.title = "Cola"
        x.field_names = ["numero","name","cantidad","codigo"] 
        for i,client in enumerate(self.cola):
            x.add_row( [i, client.name, client.cant, client.code] )
        print(x)

class Resto:
    def __init__(self):
        self.mesas = []
        self.hists = {}
        self.levantadas = []

    def add_hist(self,hist,hist_id,media,dispersion):
        self.hists[f"{hist_id}"] =  {"media":media,"dispersion":dispersion,"hist":hist/sum(hist),"hist_acum":np.cumsum(hist/sum(hist))} 

    def add_mesa(self,name="",capacidad=[],t_in=dt.datetime.today(),state="vacia",hist_id="hist_01",client=None):
        if name=="":
            name = f"mesa_{len(self.mesas+1):02d}"
        self.mesas.append( Mesa(name=name,capacidad=capacidad,t_in=t_in,state=state,hist_id=hist_id,client=client) )

    def actualizar_levantadas(self,now,verbose=False):
        if verbose: print(f"Actualizando levantadas en mesas")
        levantadas = []
        for i,mesa in enumerate(self.mesas):
            if mesa.state == 'ocupada':
                if ((now - mesa.t_in).total_seconds())/60 > self.levantadas[i][0] : 
                    t_out = mesa.t_in + dt.timedelta(minutes=self.levantadas[i][0])
                    if verbose: print(f"    Se levanto mesa:{mesa.name}, con cliente:{mesa.client.name} a las:{t_out}")
                    levantadas.append( [mesa.client.cant, mesa.client.t_llegada, mesa.t_in, t_out, mesa.t_in - mesa.client.t_llegada, t_out - mesa.t_in, t_out - mesa.client.t_llegada] )
                    (self.levantadas[i]).pop(0)
                    mesa.state = 'vacia'
        return levantadas

    def actualizar_sentadas(self,cola,now,verbose=False):
        if verbose: print("Actualizando sentadas")
        mesas_vacias = list(filter(lambda mesa:mesa.state=='vacia', self.mesas))
            
        if mesas_vacias:
            if cola.cola:
                new_cola = []
                for i,client in enumerate(cola.cola):
                    mesas_validas = list(filter(lambda mesa: (mesa.state=='vacia')and(client.cant in mesa.capacidad), mesas_vacias))            
                    if mesas_validas:
                        mesa = random.choice(mesas_validas)
                        mesa.state, mesa.t_in, mesa.client = 'ocupada', now, client
                        if verbose: print(f"    Se sento al cliente:{client.name} en la mesa:{mesa.name}")
                    else:
                        new_cola.append(client)
                        if verbose: print(f"    No hay mesas disponibles (de:{client.cant}) para el cliente:{client.name}")
                cola.cola = new_cola
            else:
                if verbose: print("    No hay clientes en la cola")
        else:
            if verbose: print("    No hay mesas vacias")

    def print_resto(self,hists=False):
        x = PrettyTable()
        x.title = "Mesas"
        x.field_names = ["name", "capacidad", "state","t_in", "hist_id"]
        for mesa in self.mesas:
            if mesa.state == "vacia":
                x.add_row( [mesa.name, mesa.capacidad , mesa.state, "-", mesa.hist_id] )
            if mesa.state == "ocupada":
                x.add_row( [mesa.name, mesa.capacidad , mesa.state, mesa.t_in.strftime("%H:%M"), mesa.hist_id] )
        print(x)
        if hists:
            x = PrettyTable()
            x.title = "Histogramas"
            x.field_names = ["hist_id","len(counts)","len(couns_acum)"]
            for hist in self.hists:
                x.add_row( [hist["hist_id"], len(hist["hist"]), len(hist["hist_acum"]) ] )
            print(x)

# ------------------------------------------------------------------------------
# Auxiliar Functions
# ------------------------------------------------------------------------------

def load_resto(cant_mesas=20,file="input_jsons/resto.json"):
    resto = Resto()
    now = dt.datetime.today()
    with open(file, 'r') as f:
        resto_dic = json.load(f)
        i = 0
        if cant_mesas > resto_dic["cant_mesas"] :
            print(f"ERROR: Max_mesas:{resto['cant_mesas']}, proceding with less mesas")
        while i < cant_mesas and i < resto_dic["cant_mesas"]:
            mesa = resto_dic["mesas"][i]
            time = dt.datetime.strptime(mesa["t_in"],"%H:%M")
            time.replace(year=now.year, month=now.month, day=now.day)
            resto.add_mesa(name=mesa["name"], capacidad=mesa["capacidad"], state=mesa["state"], t_in=time, hist_id=mesa["hist_id"],client=None)
            i += 1
        for hist in resto_dic["hists"]:
            shape, scale = Aux.gamma_parameters(media=hist["media"], dispersion=hist["dispersion"])
            bins = np.arange(0, resto_dic["t_max_sim"], resto_dic["paso_de_tiempo"])
            gamma = np.random.gamma(shape,scale,5000)
            count, _bins = np.histogram(gamma, bins, density = True )
            count = count/sum(count)
            resto.add_hist(hist=count,hist_id=hist["hist_id"],media=hist["media"],dispersion=hist["dispersion"])
    return resto

def load_cola(cant_clients,file='input_jsons/cola.json',t_llegada=dt.datetime.today()):
    cola = Cola()
    with open(file, 'r') as f:
        cola_dic = json.load(f)
        i=0
        if cant_clients > cola_dic["cant_clients"]:
            print(f"ERROR: Max_cola:{cola_dic['cant_clients']}, proceding with less clients")
        while i < cant_clients and i < cola_dic["cant_clients"]:
            client = cola_dic["clients"][i]
            cola.add_client(name=client["name"],cant=client["cant"],t_llegada=t_llegada)
            i += 1
    return cola

def giveme_llegadas(mesas,factor_de_cantidad=4,plot=False,paso=5,proporciones=[2,1,2]):
    """ devuelve: mesas*factor_de_cantidad tuplas
                  cada tupla tiene un valor de tiempo y una
                  cantidad de personas. Las tuplas estan ordenadas en tiempo"""
    def _func_densidad_llegadas(x):
        now = dt.datetime.today()
        now = now.replace(second=0,microsecond=0)
        normalizacion = 74
        ####################################################################
        #  Entre las 01:00 y 18:30
        now = now.replace(hour=1,minute=0)
        ancho = 17*60 + 30
        if dt.timedelta() < (x - now) <= dt.timedelta(minutes=ancho):
            return (0 )/normalizacion
        ####################################################################
        # Entre las 18:30 y 19:00
        now = now.replace(hour=18,minute=30)
        ancho = 30
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            return (((pow(int(((x-now).total_seconds()/60)+1),3) ) / 2700 ) )/normalizacion
        ####################################################################
        # Entre las 19:00 y 19:30
        now = now.replace(hour=19,minute=0)
        ancho = 30
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            a=-0.2 # Cambio a pero los extremos quedan fijos
            y0, y1 = 10,20
            b = (y1 - y0 - (a*(ancho**2)) )/ancho
            xx = int(((x-now).total_seconds()/60)+1)
            return (a*pow(xx,2) + b*xx + y0 )/normalizacion
        ####################################################################
        # Entre las 19:30 y 21:00
        now = now.replace(hour=19,minute=30)
        ancho = 90
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo vertice y extremo izquierdo
            y0, xv, yv = 20, 45, 5
            a = (y0-yv) / (xv**2)
            xx = int(((x-now).total_seconds()/60)+1)
            return (a*(pow(xx-xv,2)) + yv )/normalizacion
        ####################################################################
        # Entre las 21:00 y las 22:00 
        now = now.replace(hour=21,minute=0)
        ancho = 60
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo vertice y extremo izquierdo
            y0, xv, yv = 20, 30, 30
            a = (y0-yv) / (xv**2)
            xx = int(((x-now).total_seconds()/60)+1)
            return (a*(pow(xx-xv,2)) + yv )/normalizacion
        ####################################################################
        # Entre las 22:00 y las 22:30 
        now = now.replace(hour=22)
        ancho = 30
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo extremo izquierdo y derecho
            y0,y1 = 20,15
            xx = int(((x-now).total_seconds()/60)+1)
            return (((y1-y0)/ancho)*xx + y0 )/normalizacion
        ####################################################################
        # Entre las 22:30 y las 24:00 
        now = now.replace(hour=22,minute=30)
        ancho = 90
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo extremo izquierdo y derecho
            y0,y1 = 15,5
            xx = int(((x-now).total_seconds()/60)+1)
            return (((y1-y0)/ancho)*xx + y0 )/normalizacion
            # Entre las 22:30 y las 24:00 
        now = now.replace(hour=00,minute=00)
        ancho = 120
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo extremo izquierdo y derecho
            return (0 )/normalizacion
        return (0 )/normalizacion

    def _random_date(t_max,t_min):
        t_max = t_max.timestamp()
        t_min = t_min.timestamp()
        delta = t_max - t_min
        delta = delta*np.random.random_sample()
        t = dt.datetime.fromtimestamp(t_min + delta)
        return t

    def random_cant(proporciones):
        p = np.array(proporciones)
        p = np.cumsum(p/np.sum(p))
        r = np.random.random_sample()
        for i,val in enumerate(p):
            if r < val: return i+2    

    t = []
    total = len(mesas)*factor_de_cantidad
    t_min = dt.datetime.today()
    t_min = t_min.replace(hour=18,minute=30,second=30,microsecond=0)
    t_max = t_min.replace(hour=0,minute=0,second=0,microsecond=0) + dt.timedelta(days=1)
    while len(t) < total:
        date = _random_date(t_min,t_max)
        val = _func_densidad_llegadas(date)
        altura = np.random.random_sample()
        if altura < val:
            t.append( (date,random_cant(proporciones)) )
    t = sorted(t,key=lambda tuple: tuple[0])
    if plot:
        tiempos = list(map(lambda tuple:tuple[0], t))
        Aux.plot_datetime_histogram(tiempos,paso=paso)
    return t

def giveme_levantadas(resto):
    levantadas = []
    for mesa in resto.mesas:
        media, dispersion = resto.hists[f"{mesa.hist_id}"]["media"], resto.hists[f"{mesa.hist_id}"]["dispersion"]
        shape, scale = Aux.gamma_parameters(media,dispersion)
        levantadas.append( list(np.random.gamma(shape,scale,20)) )
    return levantadas

################################################################################
# Main
################################################################################

if __name__ == "__main__":
    pass