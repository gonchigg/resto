"""
    Resto
    =====

    Provides
        1. Classes `Queue` and `Resto` to handle each.
        2. Sub-classes `Table` and `Client` to handle each.
        3. Functions as `load_resto()`, `load_queue()` to load data from .jsons.
        4. Functions as `giveme_arrivals()`, `giveme_departures` to hablde both events."""
import numpy as np
import datetime as dt
import json
import random
import scipy.ndimage
import Auxiliar as Aux
from prettytable import PrettyTable

# ------------------------------------------------------------------------------------------
# Sub-classes: table, Client.
# ------------------------------------------------------------------------------------------
class Table:
    """ Class used to simulate and handle all the data relationed to each Table.
        Parameters
        ----------
        name: string, non-optional.
            Unique identity of each Table.
        capacity: list of ints, non-optional.
            Amount of Clients thath can sit in each table.
        t_in: datetime.datetime object, non-optional.
            Time in which the Table was last ocuppied.
        hist_id: string, non-optional.
            Identification of the histogram that represents the behaving of the Table.
        status: string, non-optional.
            status of the Table belonging to the variable 'Status'.
        client: Client object, non-optional.
            Object of the client that is currently on the Table."""

    Status = ("taken", "empty", "inactive")  # All possiblle states of a Table

    def __init__(self, name, capacity, t_in, t_out, hist_id, status="empty", client=None):
        """Initialize the Class Table:"""
        self.name = name
        self.client = client
        self.capacity = capacity
        self.t_in = t_in
        self.t_out = t_out
        if status not in self.Status:
            raise ValueError("%s is not a valid title." % status)
        self.status = status
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
        t_arrival: datetime.datetime object, non-optional.
            Time at which the client arrive at the queue"""

    def __init__(self, name, code, cant,color='red', t_arrival=None):
        """Initialize the Class Client:"""
        self.name = name
        self.code = code
        self.cant = cant
        self.t_arrival = t_arrival
        self.color = color
# ------------------------------------------------------------------------------------------
# Main-Classes: Queue, Resto
#       Queue ~ List of Clients, and methods
#       Resto ~ List of Tables, and methods
# ------------------------------------------------------------------------------------------
class Queue:
    def __init__(self):
        self.queue = []
        self.arrivals_register = None
        self.colors =  ['crimson','darkgoldenrod','hotpink','teal','olivedrab','peru','violet','forestgreen','chocolate','firebrick','khaki','salmon','orchid','springgreen','maroon','fuchsia','mediumorchid','turquoise','crimson','darkslategrey']
        self.counter = 0

    def add_client(self, cant, name=None, t_arrival=dt.datetime.today()):
        codes = list(filter(lambda client: client.code, self.queue))
        code = np.random.randint(low=0, high=9999)
        while code in codes:
            code = np.random.randint(low=0, high=9999)
        if not name:
            name = f"Juan_{code:04d}"
        client = Client(name=name, code=code, cant=cant, color=self.colors[( self.counter % (len(self.colors)))], t_arrival=t_arrival)
        self.counter += 1
        self.queue.append(client)
        return client

    def update_arrivals(self, now, verbose=False):
        if verbose:
            print(f"Updating arrivals ...")
        
        def check_cond(arrivals_register,now):
            if arrivals_register != []:
                if arrivals_register[0][0] < now:
                    return True
            return False

        arrivals = []
        while check_cond(self.arrivals_register,now):
            arrival = self.arrivals_register.pop(0)
            if verbose: print(f"    Client arrived at:{arrival[0].strftime('%H:%M:%S')}, they are:{arrival[1]}")
            client = self.add_client(cant=arrival[1], t_arrival=arrival[0])
            arrivals.append(client)

    def get_state(self):
        quantities = np.array([0, 0, 0])
        for client in self.queue:
            quantities[client.cant - 2] += 1
        return quantities

    def print_queue(self):
        x = PrettyTable()
        x.title = "Queue"
        x.field_names = ["#", "name", "quantity", "code"]
        for i, client in enumerate(self.queue):
            x.add_row([i, client.name, client.cant, client.code])
        print(x)

class Resto:
    def __init__(self):
        self.tables = []
        self.hists = {}
        self.departures = []
        self.time_step = 5

    def add_hist(self, hist, hist_id, mean, deviation, smooth=True):
        if smooth:
            hist = scipy.ndimage.gaussian_filter1d(input=hist,sigma=1,mode='constant')
        self.hists[f"{hist_id}"] = { "mean": mean, "deviation": deviation, "hist": hist / sum(hist), "hist_acum": np.cumsum(hist / sum(hist)) }

    def add_table(self, name="", capacity=[], t_in=dt.datetime.today(),t_out=dt.datetime.today, status="empty", hist_id="hist_01", client=None):
        if name == "":
            name = f"table_{len(self.tables+1):02d}"
        self.tables.append(
            Table(
                name=name,
                capacity=capacity,
                t_in=t_in,
                t_out=t_out,
                status=status,
                hist_id=hist_id,
                client=client,
            )
        )

    def update_departures(self, now, verbose=False):
        if verbose:
            print(f"Updating departures on Tables ...")
        departures = []
        for i, table in enumerate(self.tables):
            if table.status == "taken":
                if ((now - table.t_in).total_seconds()) / 60 > self.departures[i][0]:
                    table.t_out = table.t_in + dt.timedelta(minutes=self.departures[i][0])
                    if verbose:
                        print(f"    Table:{table.name} has stand up, with client:{table.client.name} at:{table.t_out}")
                    departures.append( (table.client.cant, table.client.t_arrival, table.t_in, table.t_out, table.t_in - table.client.t_arrival, table.t_out - table.t_in, table.t_out - table.client.t_arrival) )
                    
                    (self.departures[i]).pop(0)
                    table.status = "empty"
        return departures

    def update_sits(self, now, queue, verbose=False):
        if verbose: print("Updating sits ...")
        empty_tables = list(filter(lambda table: table.status == "empty", self.tables))

        sits = []
        if empty_tables:  # If there are empty tables
            if queue.queue:  # If there are clients in the Queue
                new_queue = []  # New Queue wont have the Clients that have sit
                for i, client in enumerate( queue.queue ):  # For each client see if it can sit: going in order of priority
                    # Get tables where the client can sit
                    valid_tables = list(filter(lambda table: (client.cant in table.capacity), empty_tables))
                    if valid_tables:  # if there are valid tables for the client
                        table = random.choice(valid_tables)  # Choose one randomly
                        if table.t_out > client.t_arrival:
                            t_in = table.t_out + dt.timedelta(minutes=1)
                        else:
                            t_in = client.t_arrival + dt.timedelta(minutes=1)
                        table.status, table.t_in, table.client = ("taken",t_in,client)
                        sits.append(table)
                        if verbose: print(f"    Client:{client.name} sit down in table:{table.name}")
                        # now we must remove this table from the empty_tables
                        empty_tables = [ _table for _table in empty_tables if _table!=table]
                    else:  # If the Client doesn´t sit it will be in the new_queue if not he will not be
                        new_queue.append(client)
                        if verbose: print(f"    No tables available (of:{client.cant}) for client:{client.name}")
                queue.queue = new_queue
            else:
                if verbose:
                    print("    No clients in Queue")
        else:
            if verbose:
                print("    No empty Tables")
        return tuple(sits)

    def print_resto(self, hists=False):
        x = PrettyTable()
        x.title = "Tables"
        x.field_names = ["name", "capacity", "status", "t_in", "hist_id"]
        for table in self.tables:
            if table.status == "empty":
                x.add_row([table.name, table.capacity, table.status, "-", table.hist_id])
            if table.status == "taken":
                x.add_row(
                    [
                        table.name,
                        table.capacity,
                        table.status,
                        table.t_in.strftime("%H:%M"),
                        table.hist_id,
                    ]
                )
        print(x)
        if hists:
            x = PrettyTable()
            x.title = "Histograms"
            x.field_names = ["hist_id", "mean", "deviation","len(counts)", "len(counts_acum)"]
            for key in self.hists:
                x.add_row( [ key, self.hists[key]["mean"], self.hists[key]["deviation"], len(self.hists[key]["hist"]), len(self.hists[key]["hist_acum"])] )
            print(x)
# ------------------------------------------------------------------------------------------
# Auxiliar Functions
# ------------------------------------------------------------------------------------------
def load_resto(file="input_jsons/resto.json",smooth_hist=True, cant_tables=20):
    """ loads the status of the resto/bar and return an object Resto

        Parameters
        ----------
            file: string, optional. Default input_jsons/resto.json.
                File from which load data (json format), usually in input_jsons/
            cant_tables: int, optional. Default 20.
                Amount of tables to be loaded, if it is higher than available it will give the maximium available.
        Return
        ------
            resto: Resto Object
                Resto Object with all the Tables and Histograms loaded.

    """
    resto = Resto()
    now = dt.datetime.today()
    with open(file, "r") as f:
        resto_dic = json.load(f)
    resto.time_step = resto_dic["time_step"]
    # Load Tables
    i = 0
    if cant_tables > resto_dic["cant_tables"]:
        print(f"ERROR: Max_tables:{resto_dic['cant_tables']}, proceding with less tables")
    while i < cant_tables and i < resto_dic["cant_tables"]:
        table = resto_dic["tables"][i]
        time = dt.datetime.strptime(table["t_in"], "%H:%M")
        time = time.replace(year=now.year, month=now.month, day=now.day)
        resto.add_table(
            name=table["name"],
            capacity=table["capacity"],
            status=table["status"],
            t_in=time,
            t_out=time,
            hist_id=table["hist_id"],
            client=None,
        )
        i += 1
    # Load histogramas
    for hist in resto_dic["hists"]:
        shape, scale = Aux.gamma_parameters(
            mean=hist["mean"], deviation=hist["deviation"]
        )
        bins = np.arange(0, resto_dic["t_max_sim"], resto_dic["time_step"])
        gamma = np.random.gamma(shape, scale, 5000)
        count, _bins = np.histogram(gamma, bins, density=True)
        count = count / sum(count)
        resto.add_hist(hist=count, hist_id=hist["hist_id"], mean=hist["mean"], deviation=hist["deviation"],smooth=smooth_hist)
    return resto

def load_queue(file="input_jsons/queue.json", t_arrival=dt.datetime.today(), cant_clients=5):
    """ loads the status of the Queue and return an object Queue

        Parameters
        ----------
            file: string, optional. Default input_jsons/queue.json.
                File from which load data (json format), usually in input_jsons/
            t_arrival: datetime.datetime object. Default calls datetime.datetime.today()
                Time of arrival of Clients at the Queue
            cant_clients: int, optional. Default 5.
                Amount of Clients to be loaded, if it is higher than available it will give the maximium available.
        Return
        ------
            queue: Queue Object
                Queue Object with all the Clients loaded.
    """
    queue = Queue()
    with open(file, "r") as f:
        queue_dic = json.load(f)
    if cant_clients > queue_dic["cant_clients"]:
        print(
            f"ERROR: Max_queue:{queue_dic['cant_clients']}, proceding with less clients"
        )
    i = 0
    # Load clients
    while i < cant_clients and i < queue_dic["cant_clients"]:
        client = queue_dic["clients"][i]
        queue.add_client(name=client["name"], cant=client["cant"], t_arrival=t_arrival)
        i += 1
    return queue

def giveme_arrivals(tables, quantity_factor=4, plot=False, step=5, proportions=[2, 1, 2]):
    """ Returns a list with tuples representing the arrivals at the queue.
        Time arrivals are calculated with a probability function that determines the rate of incoming persons to the resto/bar.
        The amount of persons of each arrival is determined randomly with the input proportions.

        Parameters
        ----------
            tables: list of Tables objects, non-optional.
                Tables of the resto/bar
            quantity_factor: int, non-optional. Default 4.
                Determines the quantity of arrivals returned.
            plot: boolean, non-optional. Default False.
                Condition of ploting or not the histogram.
            step: int, non-optional. Default 5.
                Wifth of the histogram bins in minutes.
            proportions: list of ints. Non-optional. Default [2,1,2]
                Proportion of amount of clients in groups.
                Firts value goes for groups of 2 clients.
                Second value foes for groups of 3 clients ...

        Return
        ------
            Returns a list of tuples, where each item in list represents the arrival of a client at the Queue.
            The quantity of arrivals is len(tables)*quantity_factor.
            Each Tuple has the time as a datetime.datetime object in the first element and the amount of persons in the group in the second element.
            The list is sorted by time in ascending order.
    """

    def _func_arrivals_density(x):
        now = dt.datetime.today()
        now = now.replace(second=0, microsecond=0)
        normalizacion = 74
        ####################################################################
        #  Entre las 01:00 y 18:30
        now = now.replace(hour=1, minute=0)
        ancho = 17 * 60 + 30
        if dt.timedelta() < (x - now) <= dt.timedelta(minutes=ancho):
            return (0) / normalizacion
        ####################################################################
        # Entre las 18:30 y 19:00
        now = now.replace(hour=18, minute=30)
        ancho = 30
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            return (
                (pow(int(((x - now).total_seconds() / 60) + 1), 3)) / 2700 + 5
            ) / normalizacion
        ####################################################################
        # Entre las 19:00 y 19:30
        now = now.replace(hour=19, minute=0)
        ancho = 30
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            a = -0.2  # Cambio a pero los extremos quedan fijos
            y0, y1 = 15, 20
            b = (y1 - y0 - (a * (ancho ** 2))) / ancho
            xx = int(((x - now).total_seconds() / 60) + 1)
            return (a * pow(xx, 2) + b * xx + y0) / normalizacion
        ####################################################################
        # Entre las 19:30 y 21:00
        now = now.replace(hour=19, minute=30)
        ancho = 90
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo vertice y extremo izquierdo
            y0, xv, yv = 20, 45, 5
            a = (y0 - yv) / (xv ** 2)
            xx = int(((x - now).total_seconds() / 60) + 1)
            return (a * (pow(xx - xv, 2)) + yv) / normalizacion
        ####################################################################
        # Entre las 21:00 y las 22:00
        now = now.replace(hour=21, minute=0)
        ancho = 60
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo vertice y extremo izquierdo
            y0, xv, yv = 20, 30, 30
            a = (y0 - yv) / (xv ** 2)
            xx = int(((x - now).total_seconds() / 60) + 1)
            return (a * (pow(xx - xv, 2)) + yv) / normalizacion
        ####################################################################
        # Entre las 22:00 y las 22:30
        now = now.replace(hour=22)
        ancho = 30
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo extremo izquierdo y derecho
            y0, y1 = 20, 15
            xx = int(((x - now).total_seconds() / 60) + 1)
            return (((y1 - y0) / ancho) * xx + y0) / normalizacion
        ####################################################################
        # Entre las 22:30 y las 24:00
        now = now.replace(hour=22, minute=30)
        ancho = 90
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo extremo izquierdo y derecho
            y0, y1 = 15, 5
            xx = int(((x - now).total_seconds() / 60) + 1)
            return (((y1 - y0) / ancho) * xx + y0) / normalizacion
            # Entre las 22:30 y las 24:00
        now = now.replace(hour=00, minute=00)
        ancho = 120
        if dt.timedelta() <= (x - now) < dt.timedelta(minutes=ancho):
            # Fijo extremo izquierdo y derecho
            return (0) / normalizacion
        return (0) / normalizacion

    def _random_date(t_max, t_min):
        """ returns a random datetime.datetime between t_max and t_min"""
        t_max = t_max.timestamp()
        t_min = t_min.timestamp()
        delta = t_max - t_min
        delta = delta * np.random.random_sample()
        t = dt.datetime.fromtimestamp(t_min + delta)
        return t

    def random_cant(proportions):
        """ return a random index+2 taking into account the weights inside the array"""
        p = np.array(proportions)
        p = np.cumsum(p / np.sum(p))
        r = np.random.random_sample()
        for i, val in enumerate(p):
            if r < val:
                return i + 2

    t = []
    # total of arrivals
    total = len(tables) * quantity_factor
    t_min = dt.datetime.today()
    t_min = t_min.replace(hour=18, minute=30, second=30, microsecond=0)
    t_max = t_min.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(
        days=1
    )
    # not in all cicles it will get a valida arrival, the reason is in the escence of the probabilistic behaviour
    # loop until it has the amount of arrivals desired
    while len(t) < total:
        date = _random_date(t_min, t_max)
        val = _func_arrivals_density(date)
        altura = np.random.random_sample()
        if altura < val:
            t.append((date, random_cant(proportions)))
    t = sorted(t, key=lambda tuple: tuple[0])
    if plot:
        tiempos = list(map(lambda tuple: tuple[0], t))
        Aux.plot_datetime_histogram(tiempos, step=step)
    return t

def giveme_departures(resto):
    """ given one of the histograms in resto, it simulates the amount of time group of clients is going to be in each table
        returns a list with one sublist for each table.
        each item on the sublists has the amount of time in minutes of a groupf of clients. 
    """
    departures = []
    for table in resto.tables:
        mean, deviation = resto.hists[f"{table.hist_id}"]["mean"], resto.hists[f"{table.hist_id}"]["deviation"]
        shape, scale = Aux.gamma_parameters(mean, deviation)
        departures.append(list(np.random.gamma(shape, scale, 20)))
    return departures
############################################################################################
# Main
############################################################################################
if __name__ == "__main__":
    pass
