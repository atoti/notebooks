# Sourcing fire data
# This notebook stitches together downloaded jsons from fire.ca.gov to create several dataframes used in the main notebook.

# The underlying jsons are not provided, but one can download it for themselves from ca.fire.gov and run this notebook to create updated files.

import json  # for raw fire data

import numpy as np  # for nan
import pandas as pd  # to convert json data to dataframe
import pyarrow.feather as feather  # lightweight export of dataframe
from scipy.spatial.distance import cdist

# Loading Data
path_to_read_data = "./data"  # this data can be downloaded from ca.fire.gov; replace path as appropriate
path_to_write_data = "./data"

# Opening JSON
start = 2016
end = 2021

# initiate data with first year
with open(f"{path_to_read_data}/calfire-{start}.json") as f:
    start_data = json.load(f)
    annual_data = start_data[f"firedata{start}"]

print(f"Number of fires in {start} : {len(annual_data)}")

# add second year through final year
for year in range(start + 1, end):
    with open(f"{path_to_read_data}/calfire-{year}.json") as f:
        additional_data = json.load(f)
        new_data = additional_data[f"firedata{year}"]
        print(f"Number of fires in {year} : {len(new_data)}")
        for new_datum in new_data:
            annual_data.append(new_datum)
            
# clean and convert data to dataframe
df = pd.DataFrame.from_dict(annual_data)
df = df.loc[df["AcresBurnedDisplay"] != 0]  # removing trivial data

# create df of fire+lat+lon
fire_latlon = df.filter(["Name", "Latitude", "Longitude", "StartedDate"], axis=1)

fire_latlon["LatLon"] = [
    (x, y) for x, y in zip(fire_latlon["Latitude"], fire_latlon["Longitude"])
]

fire_latlon["When"] = pd.to_datetime(fire_latlon["StartedDate"]).dt.strftime("%Y-%m-%d")
del fire_latlon["StartedDate"]

fire_latlon["Name"] = fire_latlon["When"].astype(str) + fire_latlon["Name"]
del fire_latlon["When"]

# pull in station lat+lon
solar_df = pd.read_feather(
    "s3://data.atoti.io/notebooks/ca-solar/nsrdb_station_lat_lon.feather"
)

solar_df["LatLon"] = [
    (x, y) for x, y in zip(solar_df["Latitude"], solar_df["Longitude"])
]

# create matrix of distances
fire_station_dist = cdist(list(solar_df["LatLon"]), list(fire_latlon["LatLon"]))

fs_dist = pd.DataFrame(data=fire_station_dist, columns=fire_latlon["Name"])
dist = pd.concat([solar_df["Station"], fs_dist], axis=1)

dist_df = pd.melt(
    dist, id_vars="Station", ignore_index=False, var_name="Fire", value_name="Distance"
)

fire_loc = fire_latlon.drop("LatLon", axis=1)
fire_loc.rename(
    columns={
        "Name": "Fire",
    },
    inplace=True,
)

feather.write_feather(
    dist_df, f"{path_to_write_data}/distance.feather", compression="zstd"
)
feather.write_feather(
    fire_loc, f"{path_to_write_data}/fire_loc.feather", compression="zstd"
)

fire_data = df.filter(
    ["Name", "AcresBurnedDisplay", "StartedDate", "UpdatedDate"], axis=1
)
fire_data["StartedMonth"] = pd.to_datetime(fire_data["StartedDate"]).dt.strftime("%m")

fire_data["When"] = pd.to_datetime(fire_data["StartedDate"]).dt.strftime("%Y-%m-%d")

fire_data["UpdatedDate"] = pd.to_datetime(fire_data["UpdatedDate"])
fire_data["UpdatedDate"] = [d.date() for d in fire_data["UpdatedDate"]]

fire_data["Name"] = fire_data["When"].astype(str) + fire_data["Name"]
del fire_data["When"]

fire_data.rename(
    columns={
        "UpdatedDate": "EndedDate",
        "AcresBurnedDisplay": "AcresBurned",
        "Name": "Fire",
    },
    inplace=True,
)

feather.write_feather(
    fire_data, f"{path_to_write_data}/fire_data.feather", compression="zstd"
)