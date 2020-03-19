import os
import csv
from datetime import datetime
import plotly.graph_objs as go
from plotly import offline

from helper import calculate_active, calculate_death_rate, make_hover_txt, marker_size, get_value_as_int


class DataSet():
    def __init__(self, origin_folder):
        self.origin_folder = origin_folder

        # create geo locations dictionary (necessary for January and February months, which have no location data)
        self.geo_dic = self._make_geo_dic()

        # create list of day objects
        self.days = []
        for filename in os.scandir(self.origin_folder):
            if (filename.path.endswith(".csv")) and filename.is_file():
                self.days.append(Day(filename, self))

    def _make_geo_dic(self):
        """ uses geo_locations.csv to create a dic of geo locations based on region """
        print("Creating geo location dictionary...")
        dic = {}
        with open("geo_locations.csv") as f:
            reader = csv.reader(f)
            header_row = next(reader)  # leaving this as it lets me skip header
            # for index, column_header in enumerate(header_row):
            #     print(index, column_header
            for row in reader:
                if row[0]:
                    dic[row[0]] = {"lat": row[2],
                                        "lon": row[3]}
                else:
                    dic[row[1]] = {"lat": row[2],
                                        "lon": row[3]}
        print("Geo locations dictionary created")
        return dic

    def make_scatter_geo(self, destination):
        """ creates a scattergeo html map of each day in the destination folder
                :param destination: a valid directory where to output html files"""
        print("Starting to create files...")
        for day in self.days:
            day.make_scattergeo(destination)

        print(f"Done, files created at {os.path.abspath(destination)}")


class Day():
    """
    a class to draw from the available data
    """

    def __init__(self, filename, dataset):
        """
        Creates a Day instance
        :param filename: a file from the csse_covid_19_data/csse_covid_19_daily_reports folder
        """
        self.filename = filename
        self.dataset = dataset

        print(f"Reading file: {filename} ...")

        self.time, \
        self.regions, \
        self.confirmed, \
        self.deaths, \
        self.recovered, \
        self.lats, \
        self.lons = self.get_data()

        self.active = calculate_active(self.confirmed, self.recovered, self.deaths)
        self.death_rate = calculate_death_rate(self.confirmed, self.deaths)

        self.scatter_geo = {
            "data": [{
                "type": "scattergeo",
                "lon": self.lons,
                "lat": self.lats,
                "text": make_hover_txt(self.confirmed, self.recovered, self.deaths, self.active, self.death_rate, self.regions),
                "marker": {
                    "size": [marker_size(act) for act in self.active],
                    "cmin": 0,
                    "cmax": 1,
                    "color": self.death_rate,
                    "colorscale": "Viridis",
                    "reversescale": True,
                    "colorbar": {"title": {"text": "<b>Death rate</b><br>.",
                                           "font": {"size": 20}},
                                 },
                }
            }],

            "title": f"<b>Spread of Coronavirus on {datetime.strftime(self.time, '%d/%b/%Y')}</b><br>"
                     f"<br>"
                     f"Size of markers denotes current active cases. Hover for more info.",
        }


    def get_data(self):
        """ extracts lists of data from csv file
        :return tuple of lists of extracted values"""
        with open(self.filename) as f:
            reader = csv.reader(f)
            header_row = next(reader)  # leaving this as it lets me skip header
            # for index, column_header in enumerate(header_row):
            #     print(index, column_header

            regions, confirmed, deaths, recovered, lats, lons = [], [], [], [], [], []
            time = None

            for row in reader:
                if not time:    # on the first iteration, gets the day the file refers to
                    time_str = row[2]
                    try:
                        time = self.parse_time(time_str)
                    except:
                        continue

                try:    # if no data is missing
                    conf = get_value_as_int(row[3])
                    deat = get_value_as_int(row[4])
                    reco = get_value_as_int(row[5])

                    try:    # only try because Jan and Feb have no geo location, which is added via dataset.geo_dic
                        lat = row[6]
                        lon = row[7]
                    except IndexError:
                        try:
                            if row[0]:    # if location has region name, get that in self.geo dic
                                loc = self.dataset.geo_dic[row[0]]
                            else:
                                loc = self.dataset.geo_dic[row[1]]
                            lat = loc["lat"]
                            lon = loc["lon"]
                        except KeyError:
                            continue

                    if row[0]:
                        region = f"{row[0]}, {row[1]}"
                    else:
                        region = row[1]

                    if conf >= (reco + deat):
                        confirmed.append(conf)
                        deaths.append(deat)
                        recovered.append(reco)
                        lats.append(lat)
                        lons.append(lon)
                        regions.append(region)
                    else:
                        print(f"Inconsistent data for {region} region on {time}. Please check data source.")
                        continue


                except ValueError:
                    print(f"Missing data for {row[1]} of file {self.filename}")

        return time, regions, confirmed, deaths, recovered, lats, lons

    def parse_time(self, time_str):
        """ tries to deal with the fact the first month have inconsistently formatted time """
        try:
            time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:  # Jan is formatted differently
            if time_str[2] != "/":
                time_str = "0" + time_str
            try:
                time = datetime.strptime(time_str, "%m/%d/%y %H:%M")
            except ValueError:
                time = datetime.strptime(time_str, "%m/%d/%Y %H:%M")
        return time

    def make_scattergeo(self, destination):
        """ creates a scattergeo html map of the current day in the destination folder
        :param destination: a valid directory where to output html file"""
        html_name = f"corona{datetime.strftime(self.time, '%Y-%m-%d')}.html"

        print(f"Creating file: {os.path.join(destination, html_name)}")

        my_layout = go.Layout(title=self.scatter_geo["title"])

        fig = {"data": self.scatter_geo["data"], "layout": my_layout}

        offline.plot(fig, filename=os.path.join(destination, html_name), auto_open=False)


