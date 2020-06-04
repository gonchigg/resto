import math
import numpy as np
import matplotlib.pylab as plt
import datetime as dt

def plot_datetime_histogram(times, step, strftime_formatter="%H:%M", density=False, normalizer=1,title="",show=True):
    """
        Plot an histogram of a sequence of datetime.datetime objects

        Parameters
        ----------
            times: list of datetime.datetime objects, non-optional
                List of values on which the histogram is going to be calculates
            step: int, non-optional
                Step of time on wich the histogram is going to be divided.
            strftime_formatter: string, optional. Default:'%H:%M'
                Formatter used to show the time in the x-axes, on default shows time as HH:MM
            densitity: boolean, optional. Default False.
                If the histogram should be normalized or not."""

    def lower_p(a, p):
        return p * math.floor(a / p)

    times.sort()
    t_min, t_max = times[0], times[-1]
    r1, r2 = lower_p(t_min.minute, step), lower_p(t_max.minute, step)
    t_min, t_max = (t_min.replace(minute=r1, second=0, microsecond=0), t_max.replace(minute=r2, second=0, microsecond=0) + dt.timedelta(minutes=step),)

    t_min, t_max = t_min.timestamp(), t_max.timestamp()

    times = list(map(lambda date: date.timestamp(), times))
    bins = np.arange(start=t_min, stop=t_max, step=(step * 60))
    counts, _ = np.histogram(times, bins=bins, density=density)
    counts = counts/normalizer

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.bar( (bins[:-1] + (60 * step) / 2), counts, step * 60, color="salmon", edgecolor="black", linewidth="2")
    ax.set_xticks(bins)
    _xticks = [dt.datetime.fromtimestamp(stamp) for stamp in bins]
    _xticks = [date.strftime(strftime_formatter) for date in _xticks]
    ax.set_xticklabels(_xticks)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title(title)

    ax.grid("on")
    fig.tight_layout()
    if show: plt.show()
    return

def plot_timedelta_histogram(times, step, strftime_formatter="%H:%M", density=False, normalizer=1,title="",show=True ):


    def lower_p(a, p):
        return p * math.floor(a / p)

    times.sort()
    t0 = dt.datetime.today()
    t0 = t0.replace(hour=0,minute=0,second=0,microsecond=0)
    times = [ t0 + t for t in times]
    t_min, t_max = times[0], times[-1]
    r1, r2 = lower_p(t_min.minute, step), lower_p(t_max.minute, step)
    t_min, t_max = (t_min.replace(minute=r1, second=0, microsecond=0), t_max.replace(minute=r2, second=0, microsecond=0) + dt.timedelta(minutes=step),)

    t_min, t_max = t_min.timestamp(), t_max.timestamp()

    times = list(map(lambda date: date.timestamp(), times))
    bins = np.arange(start=t_min, stop=t_max, step=(step * 60))
    counts, _ = np.histogram(times, bins=bins, density=density)
    counts = counts/normalizer

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.bar( (bins[:-1] + (60 * step) / 2), counts, step * 60, color="salmon", edgecolor="black", linewidth="2")
    ax.set_xticks(bins)
    _xticks = [dt.datetime.fromtimestamp(stamp) for stamp in bins]
    _xticks = [date.strftime(strftime_formatter) for date in _xticks]
    ax.set_xticklabels(_xticks)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title(title)

    ax.grid("on")
    fig.tight_layout()
    if show: plt.show()
    return

def gamma_parameters(mean, deviation):
    """
        Get the parameters shape and scale of a Gamma Distribution parting from the mean and the deviation.

        Parameters
        ----------
            mean: float, non-optional
            deviation: float, non-optional

        Return
        ------
            shape: float
            scale: float"""
    shape = (float(mean) / float(deviation)) * (float(mean) / float(deviation))
    scale = float(mean) / shape
    return shape, scale
