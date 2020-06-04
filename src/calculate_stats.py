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

n = 100                    # total simulations
verbose = False
# ------------------------------------------------------------------------------------------
# Create time vector
# ------------------------------------------------------------------------------------------
step = 5  # Define time step
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)  # Starting hour
now_max = now.replace(hour=23, minute=30)                       # Ending hour
t = [] #time vector
# Build time vector
while now < now_max:
    now = now + dt.timedelta(minutes=step)
    t.append(now)
t = tuple(t)
# ------------------------------------------------------------------------------------------
# Create queue_states an client_times_register as np.array
# ------------------------------------------------------------------------------------------
queue_states = np.zeros(shape=(n,len(t),3))
client_times_register = []
# ------------------------------------------------------------------------------------------
# Initial resto and queue
# ------------------------------------------------------------------------------------------
start_resto = Resto.load_resto(file="input_jsons/empty_resto.json", cant_tables=20)
start_queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
for i in range(n):
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
    for j,now in enumerate(t):
        if verbose: print(f"\nIt´s {now.strftime('%H:%M')}")
        # Update arrivals
        queue.update_arrivals( now=now, verbose=verbose )
        # Update departures and register client times
        client_times_register.extend( resto.update_departures(now, verbose=verbose) )
        # Update sits
        resto.update_sits(now, queue, verbose=False)
        # Register queue state
        queue_states[i,j] =  queue.get_state() 
    # Simulation end
# n simulations end

# ------------------------------------------------------------------------------------------
# Ploting
# ------------------------------------------------------------------------------------------
# Plot queue state in function of time
queue_states = np.array( queue_states )
queue_states_mean = np.mean( queue_states, axis=0)
queue_states_std  = np.mean( queue_states, axis=0)
fig = plt.figure(num='queue_state',figsize=(10,6),facecolor='papayawhip',edgecolor='black')
ax = fig.add_subplot(1,1,1,facecolor='antiquewhite')
lines = []
legends = []
for i in range(3):
     lines.append(ax.errorbar(t,queue_states_mean[:,i],yerr=queue_states_std[:,i],elinewidth=1,capsize=2,capthick=0.5,linestyle='-',linewidth=2) )
     legends.append(f'{i+2} clients')
ax.legend(lines,legends,loc='best',fontsize='small',shadow=True,facecolor='palegoldenrod',edgecolor=None)
plt.grid("on")

# Plot histograms of time of arrival, time of sit and living time
Aux.plot_datetime_histogram(times=[ times[1] for times in client_times_register ], step=5, normalizer=n, title='Arrival time',show=False)
Aux.plot_datetime_histogram(times=[ times[2] for times in client_times_register ], step=5, normalizer=n, title='Sit time',show=False)
Aux.plot_datetime_histogram(times=[ times[3] for times in client_times_register ], step=5, normalizer=n, title='Living time',show=False)
#Aux.plot_timedelta_histogram(times=[ times[4] for times in client_times_register ], step=5, normalizer=1, title='Waiting time',show=True)
#Aux.plot_timedelta_histogram(times=[ times[5] for times in client_times_register ], step=5, normalizer=1, title='Sit time',show=False)
#Aux.plot_timedelta_histogram(times=[ times[6] for times in client_times_register ], step=5, normalizer=1, title='Total time',show=False)

#print( [times[4] for times in client_times_register ][1:10] )

plt.show()