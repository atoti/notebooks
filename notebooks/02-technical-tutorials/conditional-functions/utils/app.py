import os
from zipfile import ZipFile

import wget
from IPython.display import clear_output, display

import atoti as tt


def bar_custom(current, total, width=80):
    clear_output(wait=True)
    print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total))


def download_data():
    wget.download("http://data.atoti.io/notebooks/xva/data.zip", bar=bar_custom)

    for item in os.listdir("."):
        if item.endswith("zip"):
            file_name = os.path.abspath(item)
            with ZipFile(file_name, "r") as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall()


def load_tables(session):
    # Loading Monte Carlo data - vectors of simulated PL per trade and future time point
    mc = session.read_csv(
        "data/monte-carlo-data.csv",
        keys=["AsOfDate", "TradeId", "TimePoint"],
        table_name="Monte Carlo Data",
        array_separator=";",
        types={"TimePoint": tt.type.INT, "AsOfDate": tt.type.LOCAL_DATE},
    )

    # Reading future scenario date labels
    sdt = session.read_csv(
        "data/simulation-dates.csv",
        keys=["AsOfDate", "TimePoint"],
        table_name="Monte Carlo Date Labels",
        types={"TimePointDate": tt.type.LOCAL_DATE, "AsOfDate": tt.type.LOCAL_DATE},
    )

    # Reading trade attributes
    trd = session.read_csv(
        "data/trades-attributes.csv",
        keys=["AsOfDate", "TradeId"],
        table_name="Trade Attributes",
        types={
            "MaturityDate": tt.type.LOCAL_DATE,
            "BreakDate": tt.type.LOCAL_DATE,
            "AsOfDate": tt.type.LOCAL_DATE,
        },
    )

    lm = session.read_csv(
        "data/limits.csv", table_name="Limits", keys=["CounterpartyId"]
    )

    # perform table joins
    mc.join(sdt)
    mc.join(trd)
    mc.join(lm, mc["CounterpartyId"] == lm["CounterpartyId"])

    return mc


def create_hierarchies(session):
    cube = session.cubes["Monte Carlo Analytics"]

    # Type of Risk mitigants for Trade Break Date example
    cube.create_parameter_hierarchy_from_members(
        "TypeofRiskMitigant", ["No Risk Mitigant", "Trade Break Date"]
    )

    # confidence level for the PFE computation
    confidence_levels = cube.create_parameter_simulation(
        "Confidence Levels",
        measures={"Confidence Level": 0.95},
        base_scenario_name="0.95%",
    )
    confidence_levels += ("0.99%", 0.99)

    # create date hierarchy
    trade_tbl = session.tables["Trade Attributes"]
    cube.create_date_hierarchy(
        "Maturity Date Hierarchy",
        column=trade_tbl["MaturityDate"],
        levels={"Year": "yyyy", "Month": "MM", "Day": "dd"},
    )


def create_measures(session):
    cube = session.cubes["Monte Carlo Analytics"]
    l, m = cube.levels, cube.measures

    # CE definitions
    m["CE_vector"] = tt.array.positive_values(m["MtM_vector.SUM"])
    m["CE"] = tt.where(~l["TimePoint"].isnull(), m["CE_vector"])
    m["PFE"] = tt.array.quantile(
        m["CE"], m["Confidence Level"], mode="centered", interpolation="higher"
    )

    # Trade table related measures
    trade_tbl = session.tables["Trade Attributes"]
    m["NotionalUSD"] = tt.agg.sum(trade_tbl["NotionalUSD"])

    # Limit table related measures
    limits_tbl = session.tables["Limits"]
    m["Limits"] = tt.agg.sum(limits_tbl["PFE Limit"])
    m["PFE Limit"] = tt.agg.single_value(limits_tbl["PFE Limit"])


def launch_cube(getData="N"):
    # download data from xva notebook
    if getData == "Y":
        download_data()

    # Starting atoti session
    session = tt.Session()
    base_table = load_tables(session)
    cube = session.create_cube(base_table, "Monte Carlo Analytics")
    create_hierarchies(session)
    create_measures(session)

    return session, cube
