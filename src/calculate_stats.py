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

waits = []
queue_states = []
n = 100

# ------------------------------------------------------------------------------------------
# Make full simulation n times
# ------------------------------------------------------------------------------------------
for _ in range(n):
    # ------------------------------------------------------------------------------------------
    # Load resto and queue
    # ------------------------------------------------------------------------------------------
    resto = Resto.load_resto(file="input_jsons/empty_resto.json", cant_tables=20)
    queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
    # ------------------------------------------------------------------------------------------
    # Pre-calculate arrivals and departures behaviour
    # ------------------------------------------------------------------------------------------
    queue.arrivals_register = Resto.giveme_arrivals(
        resto.tables, quantitytity_factor=4, proportions=[2, 2, 3]
    )
    resto.departures = Resto.giveme_departures(resto)
    # ------------------------------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------------------------------
    step = 5  # Define time step
    now = dt.datetime.today()
    now = now.replace(hour=18, minute=30, second=0, microsecond=0)  # Starting hour
    now_max = now.replace(hour=22, minute=0)  # Ending hour
    verbose = False
    queue_state = []
    while now < now_max:
        if verbose:
            print(f"\nSON LAS {now.strftime('%H:%M')}")
        queue.update_arrivals(now=now, verbose=verbose)
        waits.extend(resto.update_departures(now, verbose=verbose))
        resto.update_sits(queue, now, verbose=verbose)
        quantities = np.array([0, 0, 0])
        for client in cola.cola:
            quantities[client.cant - 2] += 1
        queue_state.append(quantities)
        now += dt.timedelta(minutes=paso)
    queue_states.append(queue_state)

queue_state_new = []
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
    now += dt.timedelta(minutes=paso)

data = pd.DataFrame(queue_state_new)
plt.figure()
lines = plt.plot(tiempos, data)
plt.legend(iter(lines), ("2", "3", "4"))
plt.grid("on")
plt.show()

waits = np.array(waits)
# print(waits[:,4])
Aux.plot_datetime_histogram(tiempos=waits[:, 1], paso=5)
