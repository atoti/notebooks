import random
import string

import numpy as np
import pandas as pd

# attributes
asset_classes = [
    "Sovereigns and their central banks",
    "Non-central government public sector entities",
    "Multilateral development banks",
    "Banks",
    "Securities firms",
    "Corporates",
    "Regulatory retail portfolios",
]
products = ["Loans", "Debt securities", "Other investments"]
maturity_buckets = [
    ">1y",
    "1 year ≤ residual maturity < 2 years",
    "2 years ≤ residual maturity < 5 years",
    "5 years ≤ residual maturity < 10 years",
    "> 10 years",
]
business_units = [
    "Personal Banking",
    "Commercial & Business Banking",
    "Wholesale Banking",
    "Asset & Wealth Management",
]
pd_bucket = [
    "0.00 to < 0.15",
    "0.15 to < 0.25",
    "0.25 to < 0.50",
    "0.50 to < 0.75",
    "0.75 to < 2.50",
    "2.50 to < 10.00",
    "10.00 to < 100",
    "100 default",
]
legal_entities = ["iBank Finance Ltd", "iBank filial", "iBank CIB"]
dates = [
    x.strftime("%Y-%m-%d")
    for x in pd.date_range(start="1/1/2020", periods=12, freq="M")
]

# number of positions in a set
num = 1000

# technical function to pick an item from a list
def pick_item(i, l):
    return l[i % len(l)]


# random trade_id generator
def generate_trade_id():
    letters = string.digits
    return "".join(random.choice(letters) for i in range(6))


# set of positions
def generate_positions(num=num, date=dates[0]):
    df = pd.DataFrame(
        columns=[
            "asset_classes",
            "products",
            "maturity_buckets",
            "business_units",
            "pd_bucket",
            "legal_entities",
            "transaction_id",
        ]
    )

    for i in range(num):
        new_position = {
            "asset_classes": pick_item(i, asset_classes),
            "products": pick_item(i, products),
            "maturity_buckets": pick_item(i, maturity_buckets),
            "business_units": pick_item(i, business_units),
            "pd_bucket": pick_item(i, pd_bucket),
            "legal_entities": pick_item(i, legal_entities),
            "transaction_id": "transaction_" + str(generate_trade_id()),
        }

        df = df.append(new_position, ignore_index=True)

    exposures = np.random.uniform(low=0, high=1000, size=(num,))
    multipliers = np.random.uniform(low=0.15, high=0.6, size=(num,))
    df["exposure"] = exposures
    df["RWA"] = exposures * multipliers
    df["reporting_date"] = date
    return df


def apply_noise(df):
    df["exposure"] = df["exposure"] * np.random.normal(1, 0.1, size=(df.shape[0],))
    df["RWA"] = df["RWA"] * np.random.normal(1, 0.1, size=(df.shape[0],))
    return df



def generate_sample_data():
    sample_data = pd.DataFrame()


    # initial set of positions - first date
    df = generate_positions()

    sample_data = sample_data.append(df)

    # all other dates
    for d in dates[1:]:
        df["reporting_date"] = d
        df = apply_noise(df)
        sample_data = sample_data.append(df)

    # new trades for iBank CIB
    for d in dates[11:]:
        df = generate_positions(num=100, date=d)
        df["legal_entities"] = "iBank CIB"
        sample_data = sample_data.append(df)

    # higher RWA for iBank CIB
    sample_data["RWA"] = sample_data.apply(
        lambda x: x["RWA"] * 1.5
        if x["legal_entities"] == "iBank CIB" and x["reporting_date"] == dates[-1]
        else x["RWA"],
        axis=1,
    )
    
    return sample_data

sample_data = generate_sample_data()
sample_data.to_csv("sample_data.csv", index = False)