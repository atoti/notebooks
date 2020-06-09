import folium
from folium.plugins import MarkerCluster
import pandas

import warnings

warnings.filterwarnings("ignore")


def build_stores_map(
    competitor_stores_df: pandas.DataFrame, stores_df: pandas.DataFrame
) -> folium.Map:
    competitors_map = folium.Map(
        location=[
            competitor_stores_df["CompetitorStoreLatitude"].mean(),
            competitor_stores_df["CompetitorStoreLongitude"].mean(),
        ],
        zoom_start=7,
    )
    # creating a Marker for each point in df_sample. Each point will get a popup with their zip
    mc = MarkerCluster()
    for index, row in competitor_stores_df.iterrows():
        lat = row["CompetitorStoreLatitude"]
        lon = row["CompetitorStoreLongitude"]
        company = row["CompetitorStoreCompany"]
        city = row["CompetitorStoreAdress"]
        mc.add_child(
            folium.Marker(
                location=[lat, lon],
                popup=company + "@" + city + "[" + str(lat) + ";" + str(lon) + "]",
            )
        )

    competitors_map.add_child(mc)

    mm = MarkerCluster()
    for index, row in stores_df.iterrows():
        lat = row["Latitude"]
        lon = row["Longitude"]
        company = row["Company"]
        city = row["Adress"]
        mm.add_child(
            folium.Marker(
                location=[lat, lon],
                popup=company + "@" + city + "[" + str(lat) + ";" + str(lon) + "]",
                icon=folium.Icon(color="red", icon="info-sign"),
            )
        )
    competitors_map.add_child(mm)

    return competitors_map


from math import pi, sqrt, sin, cos, atan2


def haversine(lat1: float, long1: float, lat2: float, long2: float) -> float:

    degree_to_rad = float(pi / 180.0)

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(
        lat2 * degree_to_rad
    ) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = 6367 * c

    return km


def create_stores_distances_matrix(
    stores_df: pandas.DataFrame, competitor_stores_df: pandas.DataFrame
) -> pandas.DataFrame:
    stores_distances_matrix = pandas.merge(
        competitor_stores_df.assign(key=0), stores_df.assign(key=0), on="key"
    )
    stores_distances_matrix["Competitor distance KM"] = stores_distances_matrix.apply(
        lambda row: haversine(
            row["Latitude"],
            row["Longitude"],
            row["CompetitorStoreLatitude"],
            row["CompetitorStoreLongitude"],
        ),
        axis=1,
    )

    return stores_distances_matrix
