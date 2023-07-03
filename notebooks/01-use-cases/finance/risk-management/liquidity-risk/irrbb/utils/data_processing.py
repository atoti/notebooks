import uuid
import pandas as pd


def getArrayValue(arrValue):
    """
    This function takes in a String delimited by ';' and converts it into a Python list containing float values.

    Args:
        arrValue: String containing float values delimited by ';'. E.g. 1,2.35;2.35;2.35;2.35;1.85;1.85;1.85;

    Returns:
        A list of float values.
    """
    arrValue = arrValue.str.split(";")
    arrValue = arrValue.apply(lambda x: [float(i) for i in x])

    return arrValue


def load_data(session, tbls):
    """
    This function loads data for the tables in the trade cube.
    - IRDelta
    - IRVega
    - SIDelta
    - Cashflow
    - Historical Risk Factor
    - Historical Dates
    - Tenors

    Sensitivities data (IRDelta, IRVega, SIDelta, Cashflow) will also be loaded into the TradeBase table.
    Historical Risk Factor data will be processed to include the value shifted by 10 historical dates.

    Args:
        session: Current Atoti session
        tbls: Table object instantiated for session
    """
    ############
    # Data loading
    ############
    # trade base and trade attributes
    tbls.tradeAttributeTbl.load_csv(
        "s3://data.atoti.io/notebooks/irrbb/TradeAttributes.csv"
    )

    # Sensitivities - IRDelta, SIDelta, IRVega, Cashflow
    # loading sensitivities data will also trigger data loading into TradeBase table
    loadSensitivity(
        tbls.tradeBaseTbl,
        tbls.irDeltaTbl,
        "https://data.atoti.io/notebooks/irrbb/IRDelta.csv",
        "DeltaSensitivities",
    )
    loadSensitivity(
        tbls.tradeBaseTbl,
        tbls.siDeltaTbl,
        "https://data.atoti.io/notebooks/irrbb/SIDelta.csv",
        "SIDeltaSensitivities",
    )
    loadSensitivity(
        tbls.tradeBaseTbl,
        tbls.irVegaTbl,
        "https://data.atoti.io/notebooks/irrbb/IRVega.csv",
        "VegaSensitivities",
    )
    loadSensitivity(
        tbls.tradeBaseTbl,
        tbls.nmrCashFlowTbl,
        "https://data.atoti.io/notebooks/irrbb/NMRCashFlow.csv",
        "CashFlowValues",
    )

    tbls.portfolioTbl.load_csv("s3://data.atoti.io/notebooks/irrbb/BookParentChild.csv")

    # historical risk factors
    histRFDF = process_historical_rf(
        "https://data.atoti.io/notebooks/irrbb/HistoricalRiskFactor.csv"
    )
    tbls.historicalRFTbl.load_pandas(histRFDF[tbls.historicalRFTbl.columns])
    tbls.historicalDateTbl.load_csv(
        "s3://data.atoti.io/notebooks/irrbb/HistoricalDates.csv"
    )

    # analysis hierarchy
    tbls.tenorsTbl.load_csv("s3://data.atoti.io/notebooks/irrbb/Tenors.csv")


def load_capitalCharge_data(tbls):
    """
    This function loads data for the tables in the Capital Charge cube.
    - Optionality Charge
    - Other APRA Amount
    - Historical ICC

    Historical ICC will be processed to derive:
    - 1PeriodLastICCValue (ICCValue)
    - 2PeriodLastICCValue (ICCValue of the previous day)
    - 3PeriodLastICCValue (ICCValue of 2 days ago)
    - AvgLast3ICC (Average of the above 3 values)

    Args:
        tbls: Table object instantiated for session
    """
    tbls.optionalityChargeTbl.load_csv(
        "s3://data.atoti.io/notebooks/irrbb/OptionalityCharge.csv"
    )
    tbls.otherAPRAAmtTbl.load_csv(
        "s3://data.atoti.io/notebooks/irrbb/OtherAPRAAmount.csv"
    )

    hist_icc_df = process_historical_icc(
        "https://data.atoti.io/notebooks/irrbb/HistoricalICC.csv"
    )
    tbls.historcialICCTbl.load_pandas(hist_icc_df[tbls.historcialICCTbl.columns])


def loadSensitivity(tradeTbl, sensiTbl, filepath, vectorField):
    """
    This function pre-process the sensitivity data to load into the TradeBase table as well as the respective sensitivity table.

    Only cashflows will have the column 'CashflowKey'. The rest of the sensitivities will take the default value of '-' for 'CashflowKey'.

    Args:
        tradeTbl: Reference for TradeBase table
        sensiTbl: Reference for Sensitivity table
        filepath: Path to source file
        vectorField: The DataFrame column containing the list of values delimited by ';'
    """

    df = pd.read_csv(filepath)
    df["AsOfDate"] = pd.to_datetime(df["AsOfDate"]).dt.date
    df[vectorField] = getArrayValue(df[vectorField])

    if "CashflowKey" not in df.columns:
        df["CashflowKey"] = "-"

    tradeTbl.load_pandas(df[tradeTbl.columns])
    sensiTbl.load_pandas(df[sensiTbl.columns])


def process_historical_rf(filepath):
    """
    This function pre-process the sensitivity data to load into the TradeBase table as well as the respective sensitivity table.

    Only cashflows will have the column 'CashflowKey'. The rest of the sensitivities will take the default value of '-' for 'CashflowKey'.

    Args:
        tradeTbl: Reference for TradeBase table
        sensiTbl: Reference for Sensitivity table
        filepath: Path to source file
        vectorField: The DataFrame column containing the list of values delimited by ';'
    """
    historical_df = pd.read_csv(filepath)
    historical_df["AsOfDate"] = pd.to_datetime(historical_df["AsOfDate"]).dt.date
    historical_df["RFValue"] = getArrayValue(historical_df["RFValue"])

    # note that the date is arranged in descending order
    # No previous value for oldest 10 days, therefore we remove the first 10 values of RF
    # remove oldest 10 days in historical date as well
    historical_df["PrevRFValue"] = historical_df["RFValue"].apply(lambda x: x[10:])
    historical_df["RFValue"] = historical_df["RFValue"].apply(lambda x: x[:-10])

    return historical_df


def process_historical_icc(filepath):
    """
    This function computes the 1st, 2nd and 3rd period of the last ICC value and the average of the three values.


    Historical ICC will be processed to derive:
    - 1PeriodLastICCValue (ICCValue)
    - 2PeriodLastICCValue (ICCValue of the previous day)
    - 3PeriodLastICCValue (ICCValue of 2 days ago)
    - AvgLast3ICC (Average of the above 3 values)

    Args:
        filepath: Path of the Historical ICC data file
    """
    hist_icc_df = pd.read_csv(filepath)
    hist_icc_df["AsOfDate"] = pd.to_datetime(hist_icc_df["AsOfDate"]).dt.date
    hist_icc_df["ICCcalculationDate"] = pd.to_datetime(
        hist_icc_df["ICCcalculationDate"]
    ).dt.date
    hist_icc_df["1PeriodLastICCValue"] = hist_icc_df["ICCValue"]
    hist_icc_df["2PeriodLastICCValue"] = hist_icc_df["ICCValue"].shift(-1)
    hist_icc_df["3PeriodLastICCValue"] = hist_icc_df["ICCValue"].shift(-2)
    hist_icc_df["AvgLast3ICC"] = hist_icc_df[
        ["1PeriodLastICCValue", "2PeriodLastICCValue", "3PeriodLastICCValue"]
    ].mean(axis=1)

    return hist_icc_df
