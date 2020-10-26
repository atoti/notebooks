import pandas as pd
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import scipy.stats as stats


def augmented_dickey_fuller_statistics(
    coin, metric_name, time_series, diff_order, _diff
):
    global full_diff_df
    result = adfuller(time_series)
    if result[1] < 0.05:
        return _diff, time_series
    else:
        print(
            coin,
            metric_name, "p-value: %f" % result[1],
            "There is unit root (Cannot reject null hypothesis) - Repeat differencing",
        )

        diff_order += 1
        differencing = time_series.diff()

        diff_df = differencing.reset_index()
        diff_df["order"] = diff_order
        diff_df.set_index(["coin_symbol", "date", "order"], inplace=True)
        axis = 1 if metric_name in diff_df.columns else 0
        _diff = pd.concat([_diff, diff_df], axis=axis, join="outer")

        return augmented_dickey_fuller_statistics(
            coin, metric_name, differencing.dropna(), diff_order, _diff
        )
    
def transform_gc_date(coin, gc_test_result, c, r, maxlag, grangercausalitytests_df, verbose):
    
    for test in ["ssr_ftest", "ssr_chi2test", "lrtest", "params_ftest"]:
        #                 print("***********", test)
        result = {"coin_symbol": coin, "x": c, "y": r, "Test name": test}

        p_values = [
            round(gc_test_result[i + 1][0][test][1], 4) for i in range(maxlag)
        ]

        # we store the p-values for each test and each lag
        result["p-value"] = ";".join(map(str, p_values))

        f_chi2 = [
            round(gc_test_result[i + 1][0][test][0], 4) for i in range(maxlag)
        ]

        if test in ["ssr_chi2test", "lrtest"]:
            result["chi2"] = ";".join(map(str, f_chi2))

            df_chi = [
                round(gc_test_result[i + 1][0][test][2], 4) for i in range(maxlag)
            ]
            result["df"] = ";".join(map(str, df_chi))
        else:
            result["F"] = ";".join(map(str, f_chi2))
            df_denom = [
                round(gc_test_result[i + 1][0][test][2], 4) for i in range(maxlag)
            ]
            result["df_denom"] = ";".join(map(str, df_denom))

            df_num = [
                round(gc_test_result[i + 1][0][test][3], 4) for i in range(maxlag)
            ]
            result["df_num"] = ";".join(map(str, df_num))

        if verbose:
            print(f"{test}  ---  Y = {r}, X = {c}, P Values = {p_values}")

        grangercausalitytests_df = grangercausalitytests_df.append(
            result, ignore_index=True
        )
        
    return grangercausalitytests_df

def autocorrelation(value):
    if value < 1.5:
        print("Positive correlation detected")
    elif value > 2.5:
        print("Negative correlation detected")
    else:
        print("No correlation detected")

def var_forecast(coin, data_stats, train_data, nobs, verbose=False):
    mod = VAR(train_data)

    selected_orders = mod.select_order().selected_orders
    max_lag = selected_orders["aic"]
    res = mod.fit(maxlags=max_lag, ic="aic")
    
    if verbose:
        print(coin, res.summary())

    fitted_df = res.fittedvalues
    # check for auto-correlation of the residual
    out = durbin_watson(res.resid)

    # collect the auto-correlatio results to be loaded into atoti later on
    for col, val in zip(train_data.columns, out):
        print((col), ":", round(val, 2), "")

        # get the residual values by taking prediction - actual
        fitted_df[f"{col} residual"] = res.resid[col] #### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        metric = fitted_df[f"{col} residual"]
        stat, p = stats.normaltest(metric)
        kurtosis = stats.kurtosis(metric)
        skewness = stats.skew(metric)
        
        print(f"coin: {coin}, metric_name: {col}, stat: {stat}, p: {p}, kurtosis: {kurtosis}, skewness: {skewness}")

        data_stats.loc[
            (data_stats["coin_symbol"] == coin) & (data_stats["metric_name"] == col),
            ["durbin_watson", "norm_stat", "norm_p", "kurtosis", "skewness"],
        ] = [val, stat, p, kurtosis, skewness]

        if verbose:
            print(
                "+++++++++++++ data_stats",
                data_stats.loc[
                    (data_stats["coin_symbol"] == coin)
                    & (data_stats["metric_name"] == col)
                ][["coin_symbol", "metric_name", "durbin_watson"]],
            )

            autocorrelation(val)

    # Get the lag order
    lag_order = res.k_ar

    if lag_order > 0:
        # Forecasting
        input_data = train_data.values[-lag_order:]
        pred = res.forecast(y=input_data, steps=nobs)

        # we generate index from the last date for a period equivalent to the size of the forecast
        last_date = train_data.tail(1).index.get_level_values("date").to_pydatetime()[0]
        date_indices = pd.date_range(
            start=last_date, periods=(nobs + 1), closed="right"
        )
        pred_df = pd.DataFrame(
            pred, index=date_indices, columns=train_data.columns,
        ).reset_index()

        return (
            fitted_df.drop(columns=train_data.columns).reset_index(),
            data_stats.loc[~data_stats["norm_stat"].isnull()],
            pred_df.rename(columns={"index": "date"}),
        )