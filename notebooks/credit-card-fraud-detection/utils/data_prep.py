import pandas as pd
from datetime import date, datetime
from haversine import Unit, haversine


def calculate_age(born):
    """
    This function computes the age for a given date to date.

    Args:
        born: Date of birth

    Returns:
        The age in integer.
    """
    born = datetime.strptime(born, "%Y-%m-%d").date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def compute_distance(cust_lat, cust_long, merch_lat, merch_long):
    """
    This function computes the distance between 2 given sets of coordinates using the haversine function.

    Args:
        cust_lat: Customer's latitude
        cust_long: Customer's longitude
        merch_lat: Merchant's latitude
        merch_long: Merchant's longitude

    Returns:
        The distance in kilometer.
    """

    cust = (cust_lat, cust_long)
    merch = (merch_lat, merch_long)
    return haversine(cust, merch, unit=Unit.KILOMETERS)


def get_cust_merch_distance(df):
    """
    This function iterates through the dataframe and computes the distance between each customer and the merchant.

    Args:
        df: Dataframe containing the columns - "lat", "long", "merch_lat", "merch_long"

    Returns:
        The list of distance in kilometer between customers and merchants.
    """

    distance = []

    for r in zip(*df.to_dict("list").values()):
        distance.append(compute_distance(r[0], r[1], r[2], r[3]))

    return distance


def is_weekend(tx_datetime):
    """
    This function checks if a date falls on weekend.

    Args:
        tx_datetime: Datetime variable

    Returns:
        0 - date falls on weekday, 1 - date falls on weekend
    """

    # Transform date into weekday (0 is Monday, 6 is Sunday)
    weekday = tx_datetime.weekday()
    # Binary value: 0 if weekday, 1 if weekend
    is_weekend = weekday >= 5

    return int(is_weekend)


# transaction has been sorted prior by the trans_date and trans_time
def get_spending_features(txn, windows_size=[1, 7, 30]):
    """
    This function computes:
        - the cumulative number of transactions for a customer for 1, 7 and 30 days
        - the cumulative average transaction amount for a customer for 1, 7 and 30 days

    Args:
        txn: grouped transactions of customer

    Returns:
        nb_trans and cust_avg_amt for each window size
    """

    # Setting trans_date as index for rolling function
    txn.index = txn.trans_date

    for size in windows_size:
        # compute the total transaction amount and the number of transactions during the window
        rolling_tx_amt = txn["amt"].rolling(f"{size}D").sum()
        roll_tx_cnt = txn["amt"].rolling(f"{size}D").count()

        # compute the average transaction amount
        avg_trans_amt = rolling_tx_amt / roll_tx_cnt

        # create as new columns
        txn[f"nb_txns_{size}_days"] = list(roll_tx_cnt)
        txn[f"avg_txns_amt_{size}_days"] = list(avg_trans_amt)

    # Reindex according to transaction IDs
    txn.index = txn.trans_num

    # And return the dataframe with the new features
    return txn


def merchant_cleanup(txns_df):
    """
    This function rounds up the longitude and latitude of the merchants and combine neighbouring merchants of the same name.

    Args:
        txn_df: The transactions dataframe containing the merchant's name, category, longitude and latitude

    Returns:
        Updated txn_df with the new latitude and longitude of the final merchant, along with an unique merchant_id for each location.
    """

    # round off the merchants longitude and latitude so that we can combine nearby merchants of same category
    txns_df["temp_long"] = txns_df["merch_long"].round()
    txns_df["temp_lat"] = txns_df["merch_lat"].round()

    # we keep the first merchant in the same area for each category
    unique_merchants = txns_df.drop_duplicates(
        # subset=["category", "temp_long", "temp_lat"], keep="first"
        subset=["merchant", "category", "temp_long", "temp_lat"],
        keep="first",
    ).copy()
    unique_merchants.rename(
        columns={
            # "merchant": "new_merchant",
            "merch_long": "new_long",
            "merch_lat": "new_lat",
        },
        inplace=True,
    )

    # create unique merchant ids for these merchants ~ could be outlet of the same brands
    unique_merchants = unique_merchants.reset_index().rename(
        columns={"index": "merchant_id"}
    )

    # set txns of the same category around the same location to the same merchants
    processed_merchants = pd.merge(
        txns_df,
        unique_merchants[
            [
                "merchant_id",
                "merchant",
                "new_long",
                "new_lat",
                "category",
                "temp_long",
                "temp_lat",
            ]
        ],
        how="left",
        on=["category", "merchant", "temp_long", "temp_lat"],
    )
    processed_merchants.drop(
        columns=["merch_lat", "merch_long", "temp_lat", "temp_long"], inplace=True
    )
    processed_merchants.rename(
        columns={
            # "new_merchant": "merchant",
            "new_long": "merch_long",
            "new_lat": "merch_lat",
        },
        inplace=True,
    )

    return processed_merchants


def compute_features(cust_df, txns_df, ignore_features=False):
    """
    This function computes additional features for machine learning:
        - age of customer
        - distance between customer and merchant
        - if transaction falls on weekend
        - if transaction happens at night
        - cumulative number of transactions in 1, 7 and 30 days
        - cumulative average transaction amount in 1, 7 and 30 days

    Args:
        cust_df: The customers dataframe
        txn_df: The transactions dataframe
        ignore_cust: Ignore features of the customer, e.g. age

    Returns:
        Updated txn_df with the new latitude and longitude of the final merchant, along with an unique merchant_id for each location.
    """
    cc_txn_df = txns_df.merge(
        cust_df, on=["ssn", "cc_num", "acct_num", "profile"], how="left"
    )

    # compute age of customer
    cc_txn_df["trans_date"] = pd.to_datetime(cc_txn_df["trans_date"])
    if ignore_features == False:
        cc_txn_df["age"] = cc_txn_df["dob"].apply(calculate_age)

    # compute distance between merchant and customer
    cc_txn_df["distance_from_cust"] = get_cust_merch_distance(
        cc_txn_df[["lat", "long", "merch_lat", "merch_long"]]
    )

    # transactions between 0500 - 2100 are encoded as normal transactions (0)
    # transactions between 2100 - 0500 are encoded as abnormal transactions (1)
    cc_txn_df["Hour"] = cc_txn_df["trans_time"].str.split(":", expand=True)[0]
    cc_txn_df["Hour"] = cc_txn_df["Hour"].astype(int)

    cc_txn_df["txn_during_night"] = 0
    cc_txn_df.loc[cc_txn_df.Hour < 5, "txn_during_night"] = 1
    cc_txn_df.loc[cc_txn_df.Hour > 21, "txn_during_night"] = 1

    # check if transactions occurred during weekday or weekend
    cc_txn_df["trans_date"] = pd.to_datetime(cc_txn_df["trans_date"])
    cc_txn_df["trans_weekend"] = cc_txn_df.trans_date.apply(is_weekend)

    # get number of txns and amount spent in the past 1, 7, 30 days
    if ignore_features == False:
        cc_txn_df = cc_txn_df.groupby("acct_num").apply(
            lambda x: get_spending_features(x, windows_size=[1, 7, 30])
        )

    cc_txn_df = cc_txn_df.sort_values(by=["trans_date", "trans_time"]).reset_index(
        drop=True
    )

    cc_txn_df.drop(columns=["Hour"], inplace=True)

    return cc_txn_df
