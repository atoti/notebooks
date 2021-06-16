# converting vehicle age to inter


def process_vehicule_age(df):
    ds = df.copy()
    ds["Vehicle_Age"] = ds["Vehicle_Age"].map(
        lambda x: 0 if x == "< 1 Year" else 1 if x == "1-2 Year" else 2
    )
    ds["Vehicle_Age"] = ds["Vehicle_Age"].astype("int")
    return ds


# changing the column type for different columns
def change_type(df):
    cols_types = {
        "str": [
            "Gender",
            "Driving_License",
            "Region_Code",
            "Previously_Insured",
            "Vehicle_Damage",
            "Policy_Sales_Channel",
        ],
        "float": ["Age", "Annual_Premium", "Vehicle_Age", "Vintage"],
        "int": ["id", "Response"],
    }

    for k, v in cols_types.items():
        for c in v:
            df[c] = df[c].astype(k)
    return df


# prepocessing steps for one hot encoding
