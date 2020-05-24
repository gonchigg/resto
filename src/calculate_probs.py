import Resto
import datetime as dt

# ------------------------------------------------------------------------------------------
# Load Resto and Queue initial values
# ------------------------------------------------------------------------------------------
resto = Resto.load_resto(file="input_jsons/empty_resto.json", cant_tables=22)
queue = Resto.load_queue(file="input_jsons/empty_queue.json", cant_clients=0)
# ------------------------------------------------------------------------------------------
# Pre-calculate arrivals and departures behaviour
# ------------------------------------------------------------------------------------------
queue.arrivals_register = Resto.giveme_arrivals(resto.tables, plot=False, step=15)
resto.departures = Resto.giveme_departures(resto)
# ------------------------------------------------------------------------------------------
# Optional: print Resto and Queue initial state
# ------------------------------------------------------------------------------------------
# resto.print_resto()
# queue.print_queue()
# ------------------------------------------------------------------------------------------
# Simulation
# ------------------------------------------------------------------------------------------
step = 5  # Define time step
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)  # Starting hour
now_max = now.replace(hour=22, minute=0)  # Ending hour
while now < now_max:
    if True:
        print(f"\nSON LAS {now.strftime('%H:%M')}")
    queue.update_arrivals(now=now, verbose=False)
    resto.update_departures(now, verbose=False)
    resto.update_sits(queue, now, verbose=False)
    # queue.calc_probs()
    now += dt.timedelta(minutes=step)
