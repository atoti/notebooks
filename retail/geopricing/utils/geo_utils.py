import folium
from folium.plugins import MarkerCluster
import pandas

import warnings

warnings.filterwarnings("ignore")


def build_shops_map(
    competitor_shops_df: pandas.DataFrame, shops_df: pandas.DataFrame
) -> folium.Map:
    competitors_map = folium.Map(
        location=[
            competitor_shops_df["CompetitorShopLatitude"].mean(),
            competitor_shops_df["CompetitorShopLongitude"].mean(),
        ],
        zoom_start=7,
    )
    # creating a Marker for each point in df_sample. Each point will get a popup with their zip
    mc = MarkerCluster()
    for index, row in competitor_shops_df.iterrows():
        lat = row["CompetitorShopLatitude"]
        lon = row["CompetitorShopLongitude"]
        company = row["CompetitorShopCompany"]
        city = row["CompetitorShopAdress"]
        mc.add_child(
            folium.Marker(
                location=[lat, lon],
                popup=company + "@" + city + "[" + str(lat) + ";" + str(lon) + "]",
            )
        )

    competitors_map.add_child(mc)

    mm = MarkerCluster()
    for index, row in shops_df.iterrows():
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

    # Using 6367 as an approximation of the radius of the average circumference of the Earth
    # instead of 6371 as a radius of the Earth, taken as the ball
    # https://rosettacode.org/wiki/Haversine_formula#.D0.9C.D0.9A-61.2F52
    earth_radius = 6367
    km = earth_radius * c

    return km


def create_shops_distances_matrix(
    shops_df: pandas.DataFrame, competitor_shops_df: pandas.DataFrame
) -> pandas.DataFrame:
    # we create the cartesian product of each (shop x competitor_shop)
    shops_distances_matrix = pandas.merge(
        competitor_shops_df.assign(key=0), shops_df.assign(key=0), on="key"
    )
    shops_distances_matrix["Competitor distance KM"] = shops_distances_matrix.apply(
        lambda row: haversine(
            row["Latitude"],
            row["Longitude"],
            row["CompetitorShopLatitude"],
            row["CompetitorShopLongitude"],
        ),
        axis=1,
    )

    return shops_distances_matrix[
        ["CompetitorShopId", "ShopId", "Competitor distance KM"]
    ]
