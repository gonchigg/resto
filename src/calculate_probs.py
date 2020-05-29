import Resto
import Probs
import datetime as dt

# ------------------------------------------------------------------------------------------
# Load Resto and Queue initial values
# ------------------------------------------------------------------------------------------
resto = Resto.load_resto(file="input_jsons/empty_resto.json",smooth_hist=True, cant_tables=6)
queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
# ------------------------------------------------------------------------------------------
# Pre-calculate arrivals and departures behaviour
# ------------------------------------------------------------------------------------------
queue.arrivals_register = Resto.giveme_arrivals(resto.tables, quantity_factor=4, plot=False, step=15)
resto.departures = Resto.giveme_departures(resto)
# ------------------------------------------------------------------------------------------
# Optional: print Resto and Queue initial state
# ------------------------------------------------------------------------------------------
# resto.print_resto()
# queue.print_queue()
# ------------------------------------------------------------------------------------------
# Simulation
# ------------------------------------------------------------------------------------------
# Simultion time vector
# *********************
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)  # Starting hour
now_max = now.replace(hour=23, minute=55)  # Ending hour
nows = []
while now < now_max:
    nows.append(now)
    now += dt.timedelta(minutes=resto.time_step)
nows = tuple(nows)
# Simulation
# **********
verbose = True
for i,now in enumerate(nows):
    if verbose: print(f"\n\n## It's {now.strftime('%H:%M')}")
    if verbose: print(f"Queueu, len:{len(queue.queue)}")
    queue.update_arrivals(now=now, verbose=True)
    resto.update_departures(now, verbose=True)
    sits = resto.update_sits(queue, now, verbose=True)
    probs = Probs.calc_probs(nows=nows[i:],time_max=dt.timedelta(hours=2),queue=queue,resto=resto,timeit=True,debug=False,verbose=True,vverbose=False)
    Probs.plot_probs(nows=nows[i:],time_max=dt.timedelta(hours=2),probs=probs,queue=queue,i=i,resto=resto,sits=sits,verbose=True,save=True,show=False)

print("")
