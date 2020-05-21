def get_last_non_zero(a):
    a = np.array(a)
    a = np.flip(a)
    for i in range(len(a)):
        if a[i] != 0:
            return a[i]

def tiempo_de_salida_mesas(cant_mesas, shapes, scales, muestras):
    tdsm = []
    for i in range(cant_mesas):
        tdsm.append( (np.random.gamma(shapes[i], scales[i], muestras)).astype(int) )
    return tdsm

def create_gammas(muestras_gamma, shapes, scales):
    gammas = []
    for i in np.arange(len(shapes)):
        gammas.append(np.random.gamma(shapes[i],scales[i],muestras_gamma))
    return gammas

def create_histograms(bins, gammas, plot, fig_num):
    histogramas_originales = []
    if plot:
        plt.figure(fig_num)
        for i in np.arange(len(gammas)):
            count, _bins, ignored = plt.hist(gammas[i], bins=bins, density=False, alpha=0.5, histtype='bar', ec='black')
            histogramas_originales.append(count/sum(count))
        plt.grid('on')
    else:
        for i in np.arange(len(gammas)):
            count, _bins = np.histogram(gammas[i], bins, density = True )
            histogramas_originales.append(count/sum(count))
    if plot: plt.show()
    return histogramas_originales

def actualizar_horarios(ax, cant_mesas, horarios, now, tdsm, Verbose, plot):
    idas = 0
    for i in range(cant_mesas):
        while ( ( horarios[i] + dt.timedelta(minutes = int(tdsm[i][0]) ) ) < now  ) :
            if Verbose: (print("    Se fue mesa:",i," a las ", ( horarios[i] + dt.timedelta(minutes = int(tdsm[i][0]) ) ).strftime("%H:%M")))
            horarios[i] = horarios[i] + dt.timedelta(minutes = int(tdsm[i][0]) )
            tdsm[i] = tdsm[i][1:]
            idas = idas + 1
        if Verbose: print("mesa: ",i, "horarios de entrada: ", (horarios[i]).strftime("%H:%M"), "proxima salida: ", ( ( horarios[i] + dt.timedelta(minutes = int(tdsm[i][0]) ) ) ).strftime("%H:%M") )
    
    if plot and idas > 0:
        string = "Se retiraron " + str(idas) + " mesas"
        ax.text(0.65, 0.05,string,transform = ax.transAxes,fontsize=14,bbox={'facecolor':'lightcoral', 'alpha':0.5, 'pad':10})   
    return horarios, tdsm, idas

def make_corrimientos(tdsm, acumular, bins, paso_de_tiempo, now, histogramas_originales, horarios, plot, Verbose, VVerbose, cant_mesas):
    if Verbose: print("En make_corrimientos ( plot =",str(plot),")")
    if plot: plt.figure()
    
    corrimientos = [   round( ( (now - horario).total_seconds() )/(60*paso_de_tiempo) )  for horario in horarios ]

    histogramas_corridos = []
    for i in range(cant_mesas):
        a = corrimientos[i] - len(histogramas_originales[i])
        if a >= -1 : # Por si me quiero caer del histograma -> lo completo con el ultimo valor
            corrimientos[i] = corrimientos[i] - ( 1 + a )
            val = histogramas_originales[i][corrimientos[i]:]
            aux = 1 - val
            aux = np.append( aux, np.zeros(corrimientos[i]) )
            aux[1] = val
            aux = aux/sum(aux)
            if acumular: aux = np.cumsum(aux)
            print("######################## aca caso especial")
            print("devuelvo aux: ",aux)
            print("a: ",a,"i: ",i)
            print("now: ",now.strftime("%H:%M"), " horario[i]: ",(horarios[i]).strftime("%H:%M"))
            print("tdsm[i]",tdsm[i])
            print("len(aux):",len(aux))
            print("distancia en pasos:",( (now - horarios[i]).total_seconds() )/(60*paso_de_tiempo))
        else:
            aux = histogramas_originales[i][corrimientos[i]:]
            if all(v == 0 for v in aux):
                val = get_last_non_zero(histogramas_originales[i])
                aux = [val, 1-val]
                print("lo corri y quedaron todos ceros, llamo a get_last_non_zero y  devuelvo")
                print("aux=",aux)
                aux = np.append( aux, np.zeros( len(histogramas_originales[i]) -2 ))
            else:
                aux = aux/sum(aux)
                aux = np.append( aux, np.zeros(corrimientos[i]) )
            if acumular: aux = np.cumsum(aux)
        histogramas_corridos.append(aux)
    
    if plot: print("falta completar plot aca")
    return histogramas_corridos

def histogramas_segunda_vuelta(acumular, plot, paso_de_tiempo, histogramas_corridos, histogramas_originales, cant_mesas):
    histogramas_con_segunda_vuelta = []
    for i in range(cant_mesas):
        histogramas_con_segunda_vuelta.append( np.convolve( histogramas_corridos[i], histogramas_originales[i], mode='full'))
    for i in range(cant_mesas):
        histogramas_con_segunda_vuelta.append( np.append(histogramas_corridos[i], np.zeros( histogramas_con_segunda_vuelta[i].shape[0] - histogramas_corridos[i].shape[0] ) ) )
    if plot:
        for i in range(cant_mesas):
            bins = np.arange(0,paso_de_tiempo*(1+histogramas_con_segunda_vuelta[i].shape[0]),paso_de_tiempo)
            histogramas_originales[i] = np.append(histogramas_originales[i], np.zeros( histogramas_con_segunda_vuelta[i].shape[0] - histogramas_originales[i].shape[0] ) )
            plt.hist( bins[:-1], bins=bins, density=True, weights = histogramas_originales[i] ,alpha=0.5, histtype='bar', ec='black')            
        for i in range(cant_mesas*2):
            bins = np.arange(0,paso_de_tiempo*(1+histogramas_con_segunda_vuelta[i].shape[0]),paso_de_tiempo)
            plt.hist( bins[:-1], bins=bins, density=True, weights = histogramas_con_segunda_vuelta[i] ,alpha=0.5, histtype='bar', ec='black')
        plt.show()
        plt.clf()
    if acumular:
        for i in range(cant_mesas*2):
            histogramas_con_segunda_vuelta[i] = np.cumsum(histogramas_con_segunda_vuelta[i])
    
    return histogramas_con_segunda_vuelta

def calc_probs(now, cant_mesas, histogramas_corridos, paso_de_tiempo, Verbose, VVerbose):
    if Verbose: print("En calc_probs")
    tiempos = []
    probs = np.zeros( (len(histogramas_corridos[0]), cant_mesas) )
    for t in np.arange(len(histogramas_corridos[0])): # Para todos los tiempos
        if VVerbose: print("    Para tiempo t:", (now + dt.timedelta(minutes= int(t)*paso_de_tiempo) ).strftime("%H:%M") )
        if VVerbose: print("        Las probabilidades mesaXmesa son:                                   ( ",end="")
        p = []
        for i in np.arange(cant_mesas): # Calcular las probabilidades para este tiempo
            if ( (histogramas_corridos[i])[t] >= 1):
                p.append(1.0)
                if t in [0]:print("en calc_prob(): histogramas_corridos[",i,"][",t,"]=",histogramas_corridos[i][t])
                if t in [0]:print("-> lo cambio por 1.0")
                if t in [0]:print("                histogramas_corridos[",i,"]= ",histogramas_corridos[i])
            else:
                p.append( (histogramas_corridos[i])[t] )
        if VVerbose: [ print( ("{:.2f}".format(_p)) , " ", end="") for _p in p]
        try:
            pb = PoiBin(p)
        except:
            print("\n ERROR: probabilities error\np: ",p,"\nt: ",t)
            for i in np.arange(cant_mesas):
                print("    histogramas_corridos[",i,"]: ",histogramas_corridos[i])
                print("    histogramas_corridos[",i,"][",t,"]: ", histogramas_corridos[i][t])
            pb = PoiBin(p)
        # Calcular las probabilidades para todas las mesas
        #if t in [0,1]: print("\n\n   t=0,1 vector de probabiliades p(mesaXmesa): ",p)
        r = []
        for cm in np.arange(1,cant_mesas+1):
            r.append(pb.pmf(int(cm)))
        r.reverse()
        r = np.cumsum(r)
        r = np.flip(r)
        r = [round(num, 2) for num in r]
        probs[t][:] = np.array(r)
        #if t in [0,1]: print("   t=0,1 vector de probabilidades r(alMenosX): ",r,end="\n\n\n")
        if VVerbose: print(")\n        Las probabilidades acumuladas de tener al menos X mesas libres son: ( ",end="")
        if VVerbose: [ print( ("{:.2f}".format(_r)) ," ", end="") for _r in r]
        if VVerbose: print(")\n",end="")
        tiempos.append( (now+dt.timedelta(minutes=int(t*paso_de_tiempo))).timestamp() )
    return tiempos, probs

def find_critical_times(Verbose, tiempos, probs, now, cant_mesas, p_max=0.8, p_min=0.2):
    critical_times = []
    for i in range(cant_mesas):
        f = interpolate.interp1d(probs[:,i], tiempos)
        try:
            t_max = f(p_max)
        except:    
            try:
                t_max = f(0.9)
            except:
                try:
                    t_max = f(0.95)
                except:
                    print("           i: ",i," probs: ", end="")
                    [ print(p," ", end="") for p in probs[:,i] ]
                    print("### ERROR: no logro encontrar f(0.95)")
                    try:
                        t_max = f(0.99)    
                    except:
                        t_max = tiempos[-1]
                        if Verbose: print("ERROR: find_critical_times(), Escala de tiempos no alcanza para encontrar el tiempo donde la probabildad alcanza ",p_max,"\n    se reemplaza t_max por ", (dt.datetime.fromtimestamp(t_max)).strftime("%H:%M") )
        try:
            t_min = f(p_min)
        except:
            t_min = now.timestamp()
            if Verbose: print("ERROR: find_critical_times(), Escala de tiempos no alcanza para encontrar el tiempo donde la probabildad alcanza ",p_min,"\n    se reemplaza t_min por ", (dt.datetime.fromtimestamp(t_min)).strftime("%H:%M") )
        width = int( (t_max-t_min)/ 60) 
        critical_times.append( (t_min, t_max, width) )
    return critical_times

def plot_state(frame, ax, fig, now, tiempos, probs, critical_times, save, show, cant_mesas, idas, colors):
    ax.set_facecolor("lavender")
    ax.set_ylim(0, 1.3)
    ax.set_ylabel("Probabilidad acumulada")
    ax.set_xlabel("Tiempo [H:M]")
    title = "Probabilidad acumulada de liberación de al menos X mesas. Hora:" + now.strftime("%H:%M")
    ax.set_title(title)
    ax.grid(True)
    
    for i in range(idas):
        colors.append(colors.pop(0))
    
    for i in range(cant_mesas):
        ax.axvline( critical_times[i][0], ymax = 0.75, linestyle='--', color=colors[i], linewidth=1)
        ax.axvline( critical_times[i][1], ymax = 0.75, linestyle='--', color=colors[i], linewidth=1)
        ax.plot( [critical_times[i][0], critical_times[i][1]], [1.1+0.05*i, 1.1+0.05*i], color=colors[i], linewidth=3)
        string = "#" + str(i+1) + " width:" + str( critical_times[i][2] )
        ax.plot(tiempos, probs[:,i], label = string ,color=colors[i], linewidth=3)
        aux = now.timestamp()
        _xticks = []
        while aux < tiempos[-1] :
            _xticks.append(aux)
            aux = aux + 60*10.0
        ax.set_xticks(_xticks)
        _xticks = [dt.datetime.fromtimestamp(stamp) for stamp in _xticks]
        _xticks = [ date.strftime("%H:%M") for date in _xticks]
        ax.set_xticklabels( _xticks )
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        #plt.legend(bbox_to_anchor=(0.9,0.7), borderaxespad=0)
        #plt.legend(bbox_to_anchor=(1.04,0,0.2,1), loc="lower left",
        #        mode="expand", borderaxespad=0, ncol=3)
        leg = ax.legend(bbox_to_anchor=(1.04,0.0,0.2,1), loc="lower left",
                borderaxespad=0, mode='expand')

    save = "images/"+str(frame)
    if save: fig.savefig(save,dpi=fig.dpi)
    if show: plt.show()
    return colors

def rounds(frame,horarios,now,cant_mesas,tdsm,paso_de_tiempo,histogramas_originales,bins,colors):
    print("\n### Son las:", now.strftime("%H:%M"))
    
    ###########################################################################################################################################
    # Se crean los graficos pertinentes, hace falta hacerlo aca porque despues se pasan como variables a las funciones que grafican
    
    fig, ax = plt.subplots(figsize=(10, 6.5)) # se crea y se define el tamaño del grafico
    plt.subplots_adjust(right=0.8) # Se corre a la izquierda el grafico para que entren los labels y no los corte

    ###########################################################################################################################################
    # Se actualizan los horarios: * horarios tiene el horario en el que se sento cada mesa
    #                             * tdsm tiene el tiempo que esta cada mesa
    #                             * Si alguna mesa ya excedio su horario la mesa se levanta y se da aviso
    horarios, tdsm, idas = actualizar_horarios(Verbose = False, plot = True, ax=ax, cant_mesas=cant_mesas, horarios=horarios, now=now, tdsm=tdsm)
    
    # Los hitogramas originales deben ser actualizados (corridos), dado que estos no tienen en cuenta el tiempo transcurrido
    # Se definen los corrimientos
    
    # Se realizan los corrimientos.
    # Poque en dos funciones distintas? no ai poque
    # Los "histogamas_corridos" vienen normalizados como DISTRIBUCIONES DE PROBABILIDAD
    histogramas_corridos = make_corrimientos(acumular = False, Verbose = False, VVerbose=False, plot = False, tdsm=tdsm, paso_de_tiempo=paso_de_tiempo, now=now, horarios=horarios, bins=bins, histogramas_originales=histogramas_originales, cant_mesas=cant_mesas)
    # Agregar histogramas corridos de segunda vuelta
    
    histogramas_con_segunda_vuelta = histogramas_segunda_vuelta(acumular = True, plot = False, paso_de_tiempo=paso_de_tiempo ,histogramas_corridos=histogramas_corridos, histogramas_originales=histogramas_originales, cant_mesas=cant_mesas)
    cant_mesas = cant_mesas*2

    # Se calculan las probabilidades en funcion del tiempo de que se levanten al menos X mesas
    tiempos, probs = calc_probs(Verbose = False, VVerbose = False, now=now, cant_mesas=cant_mesas, histogramas_corridos=histogramas_con_segunda_vuelta, paso_de_tiempo=paso_de_tiempo)
    critical_times = find_critical_times(Verbose = False, p_max = 0.8, p_min = 0.2, tiempos=tiempos, probs=probs, now=now, cant_mesas=cant_mesas)
    colors = plot_state(save=True, show=False, frame=frame, ax=ax, fig=fig, now=now, tiempos=tiempos, probs=probs, critical_times=critical_times, cant_mesas=cant_mesas, idas=idas, colors=colors)
    
    plt.clf()
    now = now + dt.timedelta(minutes=paso_de_tiempo)
    return horarios, now, tdsm, colors

def ciclo(t_max_sim,vueltas, now, horarios, tdsm, histogramas_originales, cant_mesas, paso_de_tiempo):
    bins = np.arange(0, t_max_sim, paso_de_tiempo) # bines sobre los cuales de calculan los histogramas
    colors = ['crimson','darkgoldenrod','hotpink','teal','olivedrab','peru','violet','forestgreen','chocolate','firebrick','lightblue','khaki','salmon','orchid','springgreen','maroon','fuchsia','mediumorchid','turquoise','crimson','darkslategrey']
    # En cada frame se aumenta un paso_de_tiempo (viene en minutos)
    # Se actualizan: * las curvas de probabilidad
    #                * el estado de las mesas
    #                * se realizan graficos (opcional)
    plt.rcParams.update({'figure.max_open_warning': 0})
    for frame in range(vueltas):
        horarios, now, tdsm, colors = rounds(frame=frame,horarios=horarios,now=now,cant_mesas=cant_mesas,tdsm=tdsm,paso_de_tiempo=paso_de_tiempo,histogramas_originales=histogramas_originales,bins=bins,colors=colors)
