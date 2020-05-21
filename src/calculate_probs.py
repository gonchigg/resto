import My
import datetime as dt

# Cargo mesas y cola vacias
resto = My.load_resto(file="input_jsons/resto_vacio.json", cant_mesas=22)
cola = My.load_cola(file="input_jsons/cola_vacia.json", cant_clients=0)
# Registro de llegadas y levantadas
cola.registro_de_llegadas = My.giveme_llegadas(resto.mesas, plot=False, paso=15)
resto.levantadas = My.giveme_levantadas(resto)
# resto.print_resto()
# cola.print_cola()

paso = 5  # paso de tiempo
now = dt.datetime.today()
now = now.replace(hour=18, minute=30, second=0, microsecond=0)
now_max = now.replace(hour=22, minute=0)  # + dt.timedelta(days=1)
while now < now_max:
    if True:
        print(f"\nSON LAS {now.strftime('%H:%M')}")
    cola.actualizar_llegadas(now=now, verbose=False)
    resto.actualizar_levantadas(now, verbose=False)
    resto.actualizar_sentadas(cola, now, verbose=False)
    # resto.print_resto()
    # cola.print_cola()
    # cola.calcular_probabilidades
    now += dt.timedelta(minutes=paso)
