import os
import csv
from datetime import datetime
from plotly.graph_objs import Scattergeo, Layout
from plotly import offline

from helper import calculate_active, calculate_death_rate, make_hover_txt, marker_size


class DataSet():
    def __init__(self, origin_folder):
        self.origin_folder = origin_folder

        # create list of day objects
        self.days = []
        for filename in os.scandir(self.origin_folder):
            if (filename.path.endswith(".csv")) and filename.is_file():
                if os.path.basename(filename.path)[:2] != "01" \
                        and os.path.basename(filename.path)[:2] != "02":    # TODO remove this after I figure locations for older files
                    self.days.append(Day(filename))

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

    def __init__(self, filename):
        """
        Creates a Day instance
        :param filename: a file from the csse_covid_19_data/csse_covid_19_daily_reports folder
        """
        self.filename = filename

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
                "text": make_hover_txt(self.confirmed, self.recovered, self.deaths, self.active, self.regions),
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
            #     print(index, column_header)

            regions, confirmed, deaths, recovered, lats, lons = [], [], [], [], [], []
            time = None

            for row in reader:
                if not time:
                    time = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S")
                try:
                    confirmed.append(int(row[3]))
                    deaths.append(int(row[4]))
                    recovered.append(int(row[5]))
                    lats.append(row[6])
                    lons.append(row[7])
                    if row[0]:
                        regions.append(f"{row[0]}, {row[1]}")
                    else:
                        regions.append(row[1])

                except ValueError or IndexError:
                    print(f"Missing data for {row[1]} of file {self.filename}")

        return time, regions, confirmed, deaths, recovered, lats, lons

    def make_scattergeo(self, destination):
        """ creates a scattergeo html map of the current day in the destination folder
        :param destination: a valid directory where to output html file"""
        html_name = f"corona{datetime.strftime(self.time, '%Y-%m-%d')}.html"

        print(f"Creating file: {os.path.join(destination, html_name)}")

        my_layout = Layout(title=self.scatter_geo["title"])
        fig = {"data": self.scatter_geo["data"], "layout": my_layout}

        offline.plot(fig, filename=os.path.join(destination, html_name), auto_open=False)



