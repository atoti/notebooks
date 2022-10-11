import yfinance as yf
import datetime
import datetime as dt
import pandas as pd

# initial list of symbols
symbols = [
    "AAPL",
    "MSFT",
    "AMZN",
    "TSLA",
    "GOOGL",
    "GOOG",
    "BRK-B",
    "UNH",
    "JNJ",
    "XOM",
    "NVDA",
    "META",
]


def download_tickers(symbols, duration):
    start_date = datetime.datetime.now() - datetime.timedelta(days=duration * 365)
    start_date.strftime("%Y-%m-%d")

    data = yf.download(symbols, start=start_date, end=dt.datetime.now())
    return get_historical_vector(data)


def get_historical_vector(data):

    df_close = data["Adj Close"].copy()
    # drop those stocks where there are nan values
    df_close.dropna(axis="columns", inplace=True)

    # compute returns
    df_daily_ret = df_close.diff().iloc[1:]
    df_daily_ret = df_daily_ret[(df_daily_ret == 0).sum(1) < 2]
    df_daily_ret_t = df_daily_ret.T
    df_daily_ret_t["Daily_Returns_Vector"] = df_daily_ret_t.values.tolist()
    df_daily_ret_t = (
        df_daily_ret_t[["Daily_Returns_Vector"]].rename_axis("Symbols").reset_index()
    )

    # compute daily Rate of Returns
    df_daily_ror = df_close.resample("D").last().pct_change().iloc[1:]
    df_daily_ror = df_daily_ror[(df_daily_ror == 0).sum(1) < 2]
    df_daily_ror_t = df_daily_ror.T
    df_daily_ror_t["Daily_ROR_Vector"] = df_daily_ror_t.values.tolist()
    df_daily_ror_t = (
        df_daily_ror_t[["Daily_ROR_Vector"]].rename_axis("Symbols").reset_index()
    )

    # compute monthly Rate of Returns
    df_mthly_ror = df_close.resample("M").last().pct_change().iloc[1:]
    df_mthly_ror = df_mthly_ror[(df_mthly_ror == 0).sum(1) < 2]
    df_mthly_ror_t = df_mthly_ror.T
    df_mthly_ror_t["Monthly_ROR_Vector"] = df_mthly_ror_t.values.tolist()
    df_mthly_ror_t = (
        df_mthly_ror_t[["Monthly_ROR_Vector"]].rename_axis("Symbols").reset_index()
    )

    # ensure the dateline between daily ROR and the price vectors are consistent
    left, right = df_close.align(df_daily_ror, join="outer", axis=0)
    left = left.fillna(method="ffill").iloc[1:]

    # transform daily pricing
    df_price = left.T
    df_price["Price_Vector"] = df_price.values.tolist()
    df_price = df_price[["Price_Vector"]].rename_axis("Symbols").reset_index()

    df_ror = pd.merge(df_daily_ret_t, df_daily_ror_t, on="Symbols")
    df_ror = pd.merge(df_ror, df_mthly_ror_t, on="Symbols")
    df_ror = pd.merge(df_ror, df_price, on="Symbols")

    # get vector index
    daily_dates = pd.DataFrame(data={"Historical Dates": df_daily_ror.index.to_list()})
    daily_dates = daily_dates.rename_axis("Date Index").reset_index()

    mthly_dates = pd.DataFrame(data={"Historical Dates": df_mthly_ror.index.to_list()})
    mthly_dates = mthly_dates.rename_axis("Monthly Date Index").reset_index()

    df_dates = pd.merge(daily_dates, mthly_dates, on="Historical Dates", how="left")
    df_dates = df_dates.fillna(-1)
    df_dates[["Date Index", "Monthly Date Index"]] = df_dates[
        ["Date Index", "Monthly Date Index"]
    ].astype(int)

    return df_ror, df_dates


def get_new_tickers(df, session):
    new_symbols = list(set(symbols + df["Symbols"].to_list()))
    data, date_index = download_tickers(new_symbols, 3)

    # data["Daily_Returns_Vector"] = [
    #     ",".join(map(str, l)) for l in data["Daily_Returns_Vector"]
    # ]
    # data["Daily_ROR_Vector"] = [",".join(map(str, l)) for l in data["Daily_ROR_Vector"]]
    # data["Monthly_ROR_Vector"] = [",".join(map(str, l)) for l in data["Monthly_ROR_Vector"]]
    # data["Price_Vector"] = [",".join(map(str, l)) for l in data["Price_Vector"]]

    # data.to_csv("data/historical_prices.csv", index=False)
    # date_index.to_csv("data/historical_price_index.csv", index=False)

    # data.to_csv("data/new_price.csv", index=False)
    session.tables["Price"].drop()
    session.tables["Price"].load_pandas(data)
    print("Finish loading historical pricing..")

    # load historical dates
    # date_index.to_csv("data/new_date_index.csv", index=False)
    session.tables["Historical Dates"].drop()
    session.tables["Historical Dates"].load_pandas(date_index)
    print("Finish loading historical dates..")

    # load new portfolio allocation
    session.tables["Portfolios Allocation"].load_pandas(df)
    print("Finish loading portfolio allocation...")
