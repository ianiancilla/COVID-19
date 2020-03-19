""" helper functions """
from math import sqrt

def get_value_as_int(value):
    """ takes an index of a csv row, and returns it as an int, replacing with 0 of empty
    :param value: an index of a row from a csv.reader object"""
    if not value or value == 0:
        return 0
    else:
        return int(value)

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


def make_hover_txt(confirmed, recovered, deaths, active, death_rate, regions):
    hover_txt = []
    for i in range(len(confirmed)):
        death_perc = f"{(float('{0:.3f}'.format(death_rate[i]*100)))}%"
        txt = f"<b>{regions[i]}</b><br>" \
              f"<b>{active[i]} active cases</b><br>" \
              f"Until now:<br>" \
              f"{confirmed[i]} confirmed cases,<br>" \
              f"{recovered[i]} recovered patients,<br>" \
              f"{deaths[i]} deaths<br>" \
              f"Total death rate: {death_perc}."
        hover_txt.append(txt)
    return hover_txt


def marker_size(act):
    size = 2 * sqrt(act / 3.14)
    if size >= 6:
        return size
    else:
        return 6