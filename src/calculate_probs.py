import Resto # Module used to handle the behaviour of the resto and queue
import Probs # Module used to calculate and plot probabilities
import datetime as dt

# ------------------------------------------------------------------------------------------
# Load Resto and Queue initial values
# ------------------------------------------------------------------------------------------
resto = Resto.load_resto(file="input_jsons/empty_resto.json", smooth_hist=True, cant_tables=8) # Also loads the histograms for the tables
queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
# ------------------------------------------------------------------------------------------
# Pre-calculate arrivals and departures behaviour
# ------------------------------------------------------------------------------------------
""" Arrivals will have a probabilistic behaviour given by a custom function defined inside giveme_arrivals()
    The amount of arrivals can be modified by quantity_factor but not it's time distribution """
queue.arrivals_register = Resto.giveme_arrivals(resto.tables, quantity_factor=4.5, plot=False, step=15) #quantity factor 4 or 5
# Departures will have a probabilistic behaviour given by gammas distributions with the same parameters set to the gamma distributions that build the histograms of the tables
resto.departures = Resto.giveme_departures(resto)
# ------------------------------------------------------------------------------------------
# Optional: print Resto and Queue at initial time
# ------------------------------------------------------------------------------------------
# resto.print_resto()
# queue.print_queue()
# ------------------------------------------------------------------------------------------
# Time vector used for simulation
# ------------------------------------------------------------------------------------------
now = dt.datetime.today()
now = now.replace(hour=18,minute=30,second=0,microsecond=0) # Starting hour
now_max, nows = now.replace(hour=23,minute=55), []
while now < now_max:
    nows.append(now)
    now += dt.timedelta(minutes=resto.time_step)
nows = tuple(nows)
# ------------------------------------------------------------------------------------------
# Simulation
# ------------------------------------------------------------------------------------------
for i,now in enumerate(nows):
    if True: print(f"\n\n## It's {now.strftime('%H:%M')}")
    if False: print(f"Queueu, len:{len(queue.queue)}")
    # Update Queue state: see if new clients have arrived.
    queue.update_arrivals(now, verbose=False)
    # Update Resto state: see if any client sit have left.
    resto.update_departures(now, verbose=False)
    # Update Queue and Resto state: see if there is free space for people in Queue and sit them if possible.
    sits = resto.update_sits(now, queue, verbose=False)
    """ Calculate probabilities of clients in queue.
        (probabilities are calculated using the histogram of behaviour of the tables and the state of the current resto)"""
    probs = Probs.calc_probs(nows[i:],queue,resto,time_max=dt.timedelta(hours=1,minutes=20),timeit=False,verbose=False)
    # Plot probabilities, state of Queue and Resto.
    Probs.plot_probs(nows[i:],probs,queue,resto,sits,time_max=dt.timedelta(hours=1,minutes=20),i=i,verbose=False,save=True,show=False)


