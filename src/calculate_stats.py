""" CALCULATE: 1. Amount of clients in the queue in function of time (average)
                    + (future) add the calc of dispersion
               2. Time of wait on function of arriving time
"""
import Resto
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import Auxiliar as Aux
import copy

client_times_register = [] # register of client times
queue_states = []          # register of queue state
n = 10                     # total simulations
verbose = False
# ------------------------------------------------------------------------------------------
# Create time vector
# ------------------------------------------------------------------------------------------
step = 5  # Define time step
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)  # Starting hour
now_max = now.replace(hour=23, minute=30)  # Ending hour
t = []
# Build time vector
while now < now_max:
    now = now + dt.timedelta(minutes=step)
    t.append(now)
t = tuple(t)
# ------------------------------------------------------------------------------------------
# Initial resto and queue
# ------------------------------------------------------------------------------------------
start_resto = Resto.load_resto(file="input_jsons/empty_resto.json", cant_tables=20)
start_queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
# ------------------------------------------------------------------------------------------
# Make full simulation n times
# ------------------------------------------------------------------------------------------
for _ in range(n):
    # ------------------------------------------------------------------------------------------
    # Init resto and queue
    # ------------------------------------------------------------------------------------------
    resto = copy.deepcopy(start_resto)
    queue = copy.deepcopy(start_queue)
    # ------------------------------------------------------------------------------------------
    # Pre-calculate arrivals and departures behaviour
    # ------------------------------------------------------------------------------------------
    queue.arrivals_register = Resto.giveme_arrivals(resto.tables, quantity_factor=4, proportions=[2, 2, 3])
    resto.departures = Resto.giveme_departures(resto)
    # ------------------------------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------------------------------
    queue_state = []
    for now in t:
        if verbose: print(f"\nIt´s {now.strftime('%H:%M')}")
        # Update arrivals
        queue.update_arrivals( now=now, verbose=verbose )
        # Update departures and register client times
        client_times_register.extend( resto.update_departures(now, verbose=verbose) )
        # Update sits
        resto.update_sits(  queue, now, verbose=verbose )
        # Register queue state
        queue_state.append( queue.get_state() )
    # state of queue in function of time
    queue_states.append(queue_state)

queue_state_new = []e
for t in range(len(queue_states[0])):
    queue_state_new.append(np.array([0.0, 0.0, 0.0]))
    for tanda in queue_states:
        queue_state_new[t] += (tanda[t]) / (len(queue_states[0]) + 1)

tiempos = []
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)
now_max = now.replace(hour=23, minute=20)  # + dt.timedelta(days=1)
while now < now_max:
    tiempos.append(now)
    now += dt.timedelta(minutes=step)

data = pd.DataFrame(queue_state_new)
plt.figure()
lines = plt.plot(tiempos, data)
plt.legend(iter(lines), ("2", "3", "4"))
plt.grid("on")
plt.show()

waits = np.array(waits)
# print(waits[:,4])
Aux.plot_datetime_histogram(tiempos=waits[:, 1], step=5)
