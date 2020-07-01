import folium
import pandas
import warnings
from math import pi, sqrt, sin, cos, atan2
from folium.plugins import MarkerCluster

warnings.filterwarnings("ignore")

def build_outlets_map(outlet_info: pandas.DataFrame) -> folium.Map:
    competitor_outlets_df = outlet_info[["CompetitorOutletCompany", "CompetitorOutletAdress", "CompetitorOutletLatitude.VALUE", "CompetitorOutletLongitude.VALUE"]].drop_duplicates()
    outlets_df = outlet_info[["Company", "Adress", "Latitude.VALUE", "Longitude.VALUE"]].drop_duplicates()
    
    competitors_map = folium.Map(
        location=[
            competitor_outlets_df["CompetitorOutletLatitude.VALUE"].mean(),
            competitor_outlets_df["CompetitorOutletLongitude.VALUE"].mean(),
        ],
        zoom_start=7,
    )
    # creating a Marker for each point in df_sample. Each point will get a popup with their zip
    mc = MarkerCluster()
    for index, row in competitor_outlets_df.iterrows():
        lat = row["CompetitorOutletLatitude.VALUE"]
        lon = row["CompetitorOutletLongitude.VALUE"]
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
        lat = row["Latitude.VALUE"]
        lon = row["Longitude.VALUE"]
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


def create_outlets_distances_matrix(distance_info: pandas.DataFrame) -> pandas.DataFrame:
    distance_info["Competitor distance km"] = distance_info.apply(
        lambda row: haversine(
            row["Latitude.VALUE"],
            row["Longitude.VALUE"],
            row["CompetitorOutletLatitude.VALUE"],
            row["CompetitorOutletLongitude.VALUE"],
        ),
        axis=1,
    )

    return distance_info[["CompetitorOutletId", "OutletId", "Competitor distance km"]]
