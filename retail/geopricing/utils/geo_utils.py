import folium
from folium.plugins import MarkerCluster
import pandas

import warnings

warnings.filterwarnings("ignore")


def build_outlets_map(
    competitor_outlets_df: pandas.DataFrame, outlets_df: pandas.DataFrame
) -> folium.Map:
    competitors_map = folium.Map(
        location=[
            competitor_outlets_df["CompetitorOutletLatitude"].mean(),
            competitor_outlets_df["CompetitorOutletLongitude"].mean(),
        ],
        zoom_start=7,
    )
    # creating a Marker for each point in df_sample. Each point will get a popup with their zip
    mc = MarkerCluster()
    for index, row in competitor_outlets_df.iterrows():
        lat = row["CompetitorOutletLatitude"]
        lon = row["CompetitorOutletLongitude"]
        company = row["CompetitorOutletCompany"]
        city = row["CompetitorOutletAdress"]
        mc.add_child(
            folium.Marker(
                location=[lat, lon],
                popup=company + "@" + city + "[" + str(lat) + ";" + str(lon) + "]",
            )
        )

    competitors_map.add_child(mc)

    mm = MarkerCluster()
    for index, row in outlets_df.iterrows():
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


def create_outlets_distances_matrix(
    outlets_df: pandas.DataFrame, competitor_outlets_df: pandas.DataFrame
) -> pandas.DataFrame:
    outlets_distances_matrix = pandas.merge(
        competitor_outlets_df.assign(key=0), outlets_df.assign(key=0), on="key"
    )
    outlets_distances_matrix["Competitor distance KM"] = outlets_distances_matrix.apply(
        lambda row: haversine(
            row["Latitude"],
            row["Longitude"],
            row["CompetitorOutletLatitude"],
            row["CompetitorOutletLongitude"],
        ),
        axis=1,
    )

    return outlets_distances_matrix[["CompetitorOutletId", "OutletId", "Competitor distance KM"]]
