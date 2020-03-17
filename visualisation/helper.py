""" helper functions """
from math import sqrt


def calculate_active(confirmed, recovered, deaths):
    """ creates a list of active cases, by subtracting recoveries and deaths from confirmed
    """
    active = []
    for i in range(len(confirmed)):
        active.append(confirmed[i] - recovered[i] - deaths[i])
    return active

def calculate_death_rate(confirmed, deaths):
    """ creates a list of active cases, by subtracting recoveries and deaths from confirmed"""
    death_rate = []
    for i in range(len(confirmed)):
        try:
            death_rate.append(deaths[i] / confirmed[i])
        except ZeroDivisionError:
            death_rate.append(0)
    return death_rate

def make_hover_txt(confirmed, recovered, deaths, active, regions):
    hover_txt = []
    for i in range(len(confirmed)):
        txt = f"<b>{regions[i]}</b><br>" \
              f"<b>{active[i]} active cases</b><br>" \
              f"Until now:<br>" \
              f"{confirmed[i]} confirmed cases,<br>" \
              f"{recovered[i]} recovered patients,<br>" \
              f"{deaths[i]} deaths."
        hover_txt.append(txt)
    return hover_txt

def marker_size(act):
    size = 2 * sqrt(act / 3.14)
    if size >= 6:
        return size
    else:
        return 6