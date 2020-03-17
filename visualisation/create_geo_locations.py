""" script that was run once only, used to create a list of geo locations to make files without geo locations usable
by the main script """

import os
import csv


def create_geo_locations():
    input_file = "../csse_covid_19_data/csse_covid_19_daily_reports/03-16-2020.csv"
    output_file = "geo_locations.csv"
    with open(input_file) as f:
        reader = csv.reader(f)
        header_row = next(reader)  # leaving this as it lets me skip header
        # for index, column_header in enumerate(header_row):
        #     print(index, column_header)

        province, country, lat, lon = [], [], [], [],
        for row in reader:
            province.append(row[0])
            country.append(row[1])
            lat.append(row[6])
            lon.append(row[7])
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["PROVINCE/STATE", "COUNTRY/REGION", "LATITUDE", "LONGITUDE"])
        for i in range(len(country)):
            writer.writerow([province[i].strip(), country[i].strip(), lat[i], lon[i]])
    print(f"file created at {os.path.abspath(output_file)}")
