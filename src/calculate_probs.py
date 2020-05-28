import Resto
import Probs
import datetime as dt

# ------------------------------------------------------------------------------------------
# Load Resto and Queue initial values
# ------------------------------------------------------------------------------------------
resto = Resto.load_resto(file="input_jsons/empty_resto.json", cant_tables=5)
queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
# ------------------------------------------------------------------------------------------
# Pre-calculate arrivals and departures behaviour
# ------------------------------------------------------------------------------------------
queue.arrivals_register = Resto.giveme_arrivals(resto.tables, quantity_factor=6, plot=False, step=15)
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
step = 5  # Define time step
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)  # Starting hour
now_max = now.replace(hour=20, minute=30)  # Ending hour
nows = []
while now < now_max:
    nows.append(now)
    now += dt.timedelta(minutes=step)
nows = tuple(nows)
# Simulation
# **********
for i,now in enumerate(nows):
    if True: print(f"\n## It's {now.strftime('%H:%M')}")
    queue.update_arrivals(now=now, verbose=False)
    resto.update_departures(now, verbose=False)
    resto.update_sits(queue, now, verbose=False)
    probs = Probs.calc_probs(now, now_max, queue, resto, step, timeit=True, debug=False, verbose=False, vverbose=False)
    Probs.plot_probs(nows[i:],probs,queue,i,resto,verbose=False,save=True,show=False)

print("")
