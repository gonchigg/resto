import Resto
import Probs
import datetime as dt

# ------------------------------------------------------------------------------------------
# Load Resto and Queue initial values
# ------------------------------------------------------------------------------------------
resto = Resto.load_resto(file="input_jsons/empty_resto.json", smooth_hist=True, cant_tables=15)
queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
# ------------------------------------------------------------------------------------------
# Pre-calculate arrivals and departures behaviour
# ------------------------------------------------------------------------------------------
queue.arrivals_register = Resto.giveme_arrivals(resto.tables, quantity_factor=4, plot=False, step=15) #quantity factor 4 or 5
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
    # Calculate probabilities of clients in queue.
    probs = Probs.calc_probs(nows[i:],queue,resto,time_max=dt.timedelta(hours=1,minutes=20),timeit=True,verbose=False)
    # Plot probabilities, state of Queue and Resto.
    Probs.plot_probs(nows[i:],probs,queue,i,resto,sits,time_max=dt.timedelta(hours=1,minutes=20),verbose=False,save=True,show=False)
