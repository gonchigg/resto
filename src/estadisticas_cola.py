""" CALCULAR: 1. Cantidad de gente en la cola en función del tiempo
              2. Tiempo de espera en función del tiempo de llegada
"""
import My
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import Auxiliar as Aux

esperas = []
estado_colas = []

for _ in range(100):
    # Cargo mesas y cola vacias
    resto = My.load_resto(file='resto_vacio.json',cant_mesas=20)
    cola = My.load_cola(file='cola_vacia.json',cant_clients=0)
    # Registro de llegadas y levantadas
    cola.registro_de_llegadas = My.giveme_llegadas(resto.mesas,factor_de_cantidad=4,proporciones=[2,2,3]) # Con 4 va bien
    resto.levantadas = My.giveme_levantadas(resto)

    paso=5 #paso de tiempo
    now = dt.datetime.today()
    now = now.replace(hour=18,minute=30,second=0,microsecond=0)
    now_max = now.replace(hour=23,minute=20) #+ dt.timedelta(days=1)
    verbose = False
    estado_cola = []
    while now < now_max:
        if verbose: print(f"\nSON LAS {now.strftime('%H:%M')}")
        cola.actualizar_llegadas(now=now,verbose=False)
        esperas.extend( resto.actualizar_levantadas(now,verbose=verbose) )
        resto.actualizar_sentadas(cola,now,verbose=False)
        cantidades = np.array([0,0,0])
        for client in cola.cola:
            cantidades[client.cant-2] +=1
        estado_cola.append(cantidades)
        now += dt.timedelta(minutes=paso)
    estado_colas.append(estado_cola)

estado_cola_new = []
for t in range(len(estado_colas[0])):
    estado_cola_new.append( np.array( [0.0, 0.0, 0.0]) )
    for tanda in estado_colas:
        estado_cola_new[t] += (tanda[t]) / (len(estado_colas[0])+1)

tiempos = []
now = dt.datetime.today()
now = now.replace(hour=18,minute=30,second=0,microsecond=0)
now_max = now.replace(hour=23,minute=20) #+ dt.timedelta(days=1)
while now < now_max:
    tiempos.append(now)
    now += dt.timedelta(minutes=paso)

data = pd.DataFrame(estado_cola_new)
plt.figure()
lines = plt.plot(tiempos,data)
plt.legend(iter(lines), ('2', '3', '4'))
plt.grid('on')
plt.show()

esperas = np.array(esperas)
#print(esperas[:,4])
Aux.plot_datetime_histogram(tiempos=esperas[:,1],paso=5)



    