from classes import DataSet, Day

origin_folder = "../csse_covid_19_data/csse_covid_19_daily_reports/"
destination = "./output/"

dataset = DataSet(origin_folder)
dataset.make_scatter_geo(destination)
dataset.make_choro_active(destination)
dataset.make_choro_death_rate(destination)
