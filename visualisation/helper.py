""" helper functions """
from math import sqrt
import csv


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


def make_country_dict(filename):
    """ tales a csv file with country codes, and returns a dictionary of these codes """
    print("Creating country code dictionary...")
    with open(filename) as f:
        reader = csv.reader(f)
        header_row = next(reader)

        names, iso_3 = [], []
        for row in reader:
            names.append(row[0])
            iso_3.append(row[3])

    dic = {}
    for i in range(len(names)):
        dic[names[i].lower()] = iso_3[i]

    print("Country code dictionary created successfully.")

    return dic

def make_iso_data(day):
    iso_data = {}

    for i in range(len(day.iso_3)):    # per ogni regione di un tal giorno
        current_iso = day.iso_3[i]
        if not current_iso in iso_data.keys():
            iso_data[current_iso] = {
                "time": day.time,
                "country": day.countries[i],
                "confirmed": day.confirmed[i],
                "deaths": day.deaths[i],
                "recovered": day.recovered[i],
            }
        else:
            iso_data[current_iso]["confirmed"] += iso_data[current_iso]["confirmed"]
            iso_data[current_iso]["deaths"] += iso_data[current_iso]["deaths"]
            iso_data[current_iso]["recovered"] += iso_data[current_iso]["recovered"]

    iso_iso, iso_conf, iso_rec, iso_dea, iso_act, iso_dr, iso_reg = [], [], [], [], [], [], []

    for k in iso_data:
        iso_data[k]["active"] = (iso_data[k]["confirmed"] - iso_data[k]["recovered"] - iso_data[k]["deaths"])
        try:
            iso_data[k]["death_rate"] = iso_data[k]["deaths"] / iso_data[k]["confirmed"]
        except ZeroDivisionError:
            iso_data[k]["death_rate"] = 0

        iso_conf.append(iso_data[k]["confirmed"])
        iso_rec.append(iso_data[k]["recovered"])
        iso_dea.append(iso_data[k]["deaths"])
        iso_act.append(iso_data[k]["active"])
        iso_dr.append(iso_data[k]["death_rate"])
        iso_reg.append(iso_data[k]["country"])
        iso_iso.append(k)

    return iso_iso, iso_conf, iso_rec, iso_dea, iso_act, iso_dr, iso_reg

