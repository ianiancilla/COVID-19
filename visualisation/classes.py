import os
import csv
from datetime import datetime
import plotly.graph_objs as go
from plotly import offline
from helper import calculate_active, calculate_death_rate, make_hover_txt, marker_size,\
    get_value_as_int, make_country_dict, make_iso_data


class DataSet():
    def __init__(self, origin_folder):
        self.origin_folder = origin_folder

        # create geo locations dictionary (necessary for January and February months, which have no location data)
        self.geo_dic = self._make_geo_dic()

        self.country_codes = make_country_dict("./country_codes.csv")

        # create list of day objects
        self.days = []
        for filename in os.scandir(self.origin_folder):
            if (filename.path.endswith(".csv")) and filename.is_file():
                self.days.append(Day(filename, self))

        self.max_confirmed = self._get_max_confirmed()

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

    def _get_max_confirmed(self):
        max_conf = 0
        for day in self.days:
            day_max = max(day.confirmed)
            if day_max > max_conf:
                max_conf = day_max
        return max_conf

    def make_scatter_geo(self, destination):
        """ creates a scattergeo html map of each day in the destination folder
                :param destination: a valid directory where to output html files"""
        print("Starting to create scattergeo files...")
        for day in self.days:
            day.make_scattergeo(destination)

        print(f"Done, files created at {os.path.abspath(destination)}")

    def make_choro_active(self, destination):
        """ creates a choropleth html map of each day in the destination folder, according to number of active cases
                :param destination: a valid directory where to output html files"""
        print("Starting to create active cases choropleth files...")
        for day in self.days:
            day.make_cloropleth(day.active, "Active cases",
                                min=0,
                                max=self._get_max_confirmed(),
                                destination=destination)
        print(f"Done, files created at {os.path.abspath(destination)}")

    def make_choro_death_rate(self, destination):
        """ creates a choropleth html map of each day in the destination folder, according to the total death rate
                :param destination: a valid directory where to output html files"""
        print("Starting to create death rate choropleth files...")
        for day in self.days:
            day.make_cloropleth(day.death_rate, "Death rate",
                                min=0,
                                max=1,
                                destination=destination)
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
        self.countries,\
        self.regions, \
        self.confirmed, \
        self.deaths, \
        self.recovered, \
        self.lats, \
        self.lons,\
        self.iso_3 = self.get_data()

        self.active = calculate_active(self.confirmed, self.recovered, self.deaths)
        self.death_rate = calculate_death_rate(self.confirmed, self.deaths)

        self.iso_iso, \
        self.iso_conf, \
        self.iso_rec, \
        self.iso_dea, \
        self.iso_act, \
        self.iso_dr, \
        self.iso_reg = make_iso_data(self)

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

            regions, countries, confirmed, deaths, recovered, lats, lons, iso_3 = [], [], [], [], [], [], [], []
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

                    if row[1] == "Others" or "Cruise" in row[1]:
                        iso = None
                    else:
                        iso = self.dataset.country_codes[row[1].lower()]

                    if conf >= (reco + deat):
                        confirmed.append(conf)
                        deaths.append(deat)
                        recovered.append(reco)
                        lats.append(lat)
                        lons.append(lon)
                        regions.append(region)
                        countries.append(row[1])
                        iso_3.append(iso)

                    else:
                        print(f"Inconsistent data for {region} region on {time}. Please check data source.")
                        continue


                except ValueError:
                    print(f"Missing data for {row[1]} of file {self.filename}")

        return time, countries, regions, confirmed, deaths, recovered, lats, lons, iso_3

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
        html_name = f"corona_scatter_{datetime.strftime(self.time, '%Y-%m-%d')}.html"

        print(f"Creating file: {os.path.join(destination, html_name)}")

        my_layout = go.Layout(title=self.scatter_geo["title"])

        fig = {"data": self.scatter_geo["data"], "layout": my_layout}

        offline.plot(fig, filename=os.path.join(destination, html_name), auto_open=False)

    def make_cloropleth(self, z_param, z_param_str, min, max, destination):
        """ creates a scattergeo html map of the current day in the destination folder
        :param z_param: the parameter to assign color to areas. Ex self.death_rate or sef.active
        :param z_param_str: name of the parameter
        :param min, max: integers representingthe min and max z-values"""

        html_name = f"corona_choro_{z_param_str.replace(' ','_')}_{datetime.strftime(self.time, '%Y-%m-%d')}.html"

        print(f"Creating file: {os.path.join(destination, html_name)}")

        title = f"<b>{z_param_str} of Coronavirus on {datetime.strftime(self.time, '%d/%b/%Y')}</b><br>" \
                f"<br>" \
                f"Hover on countries for more info."

        fig = go.Figure(data=go.Choropleth(
                                            locations=self.iso_iso,
                                            z=z_param,
                                            text=make_hover_txt(self.iso_conf,
                                                                  self.iso_rec,
                                                                  self.iso_dea,
                                                                  self.iso_act,
                                                                  self.iso_dr,
                                                                  self.iso_reg),
                                            colorscale='Reds',
                                            zmin=min,
                                            zmax=max,
                                            autocolorscale=False,
                                            reversescale=False,
                                            marker_line_color='darkgray',
                                            marker_line_width=0.9,
                                            colorbar_title=f"<b>{z_param_str}</b><br>",))
        fig.update_layout(
            title_text= title,
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            )
        )

        offline.plot(fig, filename=os.path.join(destination, html_name), auto_open=False)
        #fig.show()
