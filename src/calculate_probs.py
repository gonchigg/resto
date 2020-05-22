import Resto
import datetime as dt

# Cargo tables y queue vacias
resto = Resto.load_resto(file="input_jsons/resto_vacio.json", cant_tables=22)
queue = Resto.load_queue(file="input_jsons/queue_empty.json", cant_clients=0)
# Registro de llegadas y departures
queue.arrivals_register = Resto.giveme_arrivals(resto.tables, plot=False, step=15)
resto.departures = Resto.giveme_departures(resto)
# resto.print_resto()
# queue.print_queue()

resto.print_resto()

step = 5  # paso de tiempo
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)
now_max = now.replace(hour=22, minute=0)  # + dt.timedelta(days=1)
while now < now_max:
    if True:
        print(f"\nSON LAS {now.strftime('%H:%M')}")
    queue.update_arrivals(now=now, verbose=False)
    resto.update_departures(now, verbose=False)
    resto.update_sits(queue, now, verbose=False)
    # resto.print_resto()
    # queue.print_queue()
    # queue.calcular_probabilidades
    now += dt.timedelta(minutes=step)
