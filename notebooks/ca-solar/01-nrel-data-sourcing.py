# Sourcing GHI data from NREL
# This notebook can be used to download data from the 
# The National Renewable Energy Laboratory (NREL) 
# Solar Radiation Database (NSRDB).

# For this to work, first install h5pyd:
# pip3 install --user h5pyd
# Next, configure HSDS: (in shell)
# hsconfigure
# and enter at the prompt:
# hs_endpoint = https://developer.nrel.gov/api/hsds
# hs_username = None
# hs_password = None
# hs_api_key = 3K3JQbjZmWctY0xmIfSYvYgtIcM3CN0cb1Y2w9bf

# This notebook draws heavily from NREL github examples (https://github.com/NREL/hsds-examples/blob/master/notebooks/) and uses the example API key given there. Used here is the demonstation key and is rate-limited per IP.

# To get an API key, visit https://developer.nrel.gov/signup/

import sys
import time

import h5pyd  # to read from nrel server
import numpy as np
import pandas as pd
import pyarrow.feather as feather

def find_missing(lst):
    return [x for x in range(lst[0], lst[-1] + 1) if x not in lst]

# Set state, year, time of day to download
state = "California"
start = 2016
end = 2021
utctime = "20"  # selecting noon local standard time
k = 3  # keeping only 1/k^2 of the locations

remote_path = f"/nrel/nsrdb/v3/nsrdb_{start}.h5"
with h5pyd.File(remote_path, mode="r") as f:
    meta = pd.DataFrame(f["meta"][...])
    
state_meta = meta.loc[meta["state"] == bytes(state, encoding="utf-8")]
state_index = state_meta.index.values.copy()
print(f"Number of NSRDB pixels in {state} = {len(state_meta)}")

latlon_data = []
for index in state_index:
    location_id = f"station_{index:0=9d}"
    location_data = [location_id, meta["latitude"][index], meta["longitude"][index]]
    latlon_data.append(location_data)

latlon_df = pd.DataFrame(latlon_data, columns=["Station", "Latitude", "Longitude"])

lat = sorted(latlon_df.Latitude.unique())
lon = sorted(latlon_df.Longitude.unique())

# keeping only 1/k^2 of the station data
keep_lats = lat[::k]
keep_lons = lon[::k]

final_latlon = latlon_df[
    latlon_df["Latitude"].isin(keep_lats) & latlon_df["Longitude"].isin(keep_lons)
]

feather.write_feather(final_latlon, f"./data/nsrdb_station_lat_lon.feather")

for year in range(start, end):
    # Set remote destination of h5 file from nrel
    file_path = "/nrel/nsrdb/v3/nsrdb_{}.h5".format(year)
    with h5pyd.File(file_path, mode="r") as f:
        # create time indices for dataframe
        time_df = pd.DataFrame()
        time_df["datetime"] = pd.to_datetime(f["time_index"][::2].astype(str))
        time_df["time"] = [d.time() for d in time_df["datetime"]]

        # for each type of data (https://nsrdb.nrel.gov/about/u-s-data.html)
        for dset in [
            "ghi"
        ]:  # ['dni', 'wind_speed', 'wind_direction', 'dhi', 'air_temperature', 'solar_zenith_angle']:
            # access the nsrdb h5 file
            ds = f[dset]
            state_df = pd.DataFrame()

            # create numpy superset array containing all columns for current state
            lower_bound = state_index[0]
            upper_bound = state_index[-1]
            supset = (
                ds[::2, lower_bound : upper_bound + 1] / ds.attrs["psm_scale_factor"]
            )  # ::2 ---> hourly data only

            # Determine which columns to remove from superset of columns
            offset = state_index[0]
            state_list = [x - offset for x in state_index]
            remove_indices = find_missing(state_list)
            state_data = np.delete(supset, remove_indices, 1)

            # Add station labels to data
            count = 0
            for index in state_index:
                location_id = f"station_{index:0=9d}"
                state_df[location_id] = state_data[:, count]
                count += 1

            # concatenate state data with timeseries indices
            time_state_df = pd.concat([time_df, state_df], axis=1)

            # removing all data except specified UTC time
            state_noon_data = time_state_df[
                time_state_df["time"].astype(str).isin([utctime + ":00:00"])
            ]
            del state_noon_data["time"]

            # reshape data to columnar df
            melted_state_df = pd.melt(
                state_noon_data,
                id_vars=["datetime"],
                var_name="Station",
                value_name=dset,
            )

            final_state_df = melted_state_df[
                melted_state_df["Station"].isin(final_latlon["Station"])
            ]

            feather.write_feather(
                final_state_df, f"./data/nsrdb_{year}_{state}_{utctime}UTC_GHI.feather"
            )