import math
import numpy as np
import matplotlib.pylab as plt
import datetime as dt

def plot_datetime_histogram(tiempos,paso,strftime_formatter="%H:%M",density=False):
    """El vector de tiempos esta conformado por datetimes,
       paso es el paso de tiempo para los bins. El vector de tiempos
       debe estar ordenado"""
    def lower_p(a,p):
        return p*math.floor(a/p)

    t_min, t_max = tiempos[0], tiempos[-1]
    r1, r2 = lower_p(t_min.minute,paso), lower_p(t_max.minute,paso)
    t_min, t_max = t_min.replace(minute=r1,second=0,microsecond=0), t_max.replace(minute=r2,second=0,microsecond=0) + dt.timedelta(minutes=paso)
    t_min, t_max = t_min.timestamp(), t_max.timestamp()

    tiempos = list(map(lambda date: date.timestamp(),tiempos))
    bins = np.arange(start=t_min,stop=t_max,step=(paso*60))
    counts, _ = np.histogram(tiempos, bins=bins ,density=density)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.bar( (bins[:-1]+ (60*paso)/2) ,counts,paso*60,color='salmon',edgecolor='black',linewidth='2')
    ax.set_xticks(bins)
    _xticks = [ dt.datetime.fromtimestamp(stamp) for stamp in bins]
    _xticks = [ date.strftime(strftime_formatter) for date in _xticks]
    ax.set_xticklabels( _xticks )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    ax.grid('on')
    fig.tight_layout()
    plt.show()

def gamma_parameters(media,dispersion):
    shape = ( float(media)/float(dispersion) )*( float(media)/float(dispersion) )
    scale = float(media)/shape
    return shape, scale
