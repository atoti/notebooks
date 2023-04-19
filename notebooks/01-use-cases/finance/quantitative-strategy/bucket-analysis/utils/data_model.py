import atoti as tt
import pandas as pd


def table_creation(session):
    txn_tbl = session.read_csv(
        "s3://data.atoti.io/notebooks/bucket-exploration/initial_transactions.csv",
        table_name="Transaction",
        keys=["TransactionId", "Ticker", "DateTime"],
        types={
            "DateTime": tt.type.STRING,
            "PurchaseDate": tt.type.STRING,
            "Timestamp": tt.type.STRING,
        },
    )


def cube_creation(session):
    txn_tbl = session.tables["Transaction"]
    cube = session.create_cube(txn_tbl, name="TxnCube", mode="no_measures")

    # cube.shared_context["queriesResultLimit.intermediateLimit"] = -1
    # cube.shared_context["queriesResultLimit.transientLimit"] = -1


def create_model(session):
    table_creation(session)
    cube_creation(session)


def enrich_cube(session):
    txn_tbl = session.tables["Transaction"]

    sector_tbl = session.read_csv(
        "s3://data.atoti.io/notebooks/bucket-exploration/constituents.csv",
        table_name="Sector",
        keys=["Symbols"],
    )

    hist_tbl = session.read_csv(
        "s3://data.atoti.io/notebooks/bucket-exploration/bucketed_historical_pricing.csv",
        table_name="HistoricalPricing",
        keys=["Ticker", "DateTime"],
        types={"DateTime": tt.type.STRING},
    )

    txn_tbl.join(sector_tbl, txn_tbl["Ticker"] == sector_tbl["Symbols"])
    txn_tbl.join(
        hist_tbl,
        (txn_tbl["Ticker"] == hist_tbl["Ticker"])
        & (txn_tbl["DateTime"] == hist_tbl["DateTime"]),
    )


def create_measures(session):
    cube = session.cubes["TxnCube"]
    hist_tbl = session.tables["HistoricalPricing"]
    h, l, m = cube.hierarchies, cube.levels, cube.measures

    m["Volume"] = tt.agg.single_value(hist_tbl["Volume"])
    m["High"] = tt.agg.single_value(hist_tbl["High"])
    m["Low"] = tt.agg.single_value(hist_tbl["Low"])
    m["Open"] = tt.agg.single_value(hist_tbl["Open"])

    for _m in ["Volume", "High", "Low", "Open"]:
        m[_m].folder = "HistoricalMetrics"


def load_transactions(session, df):
    txn_tbl = session.tables["Transaction"]

    txn_tbl.load_pandas(df)
