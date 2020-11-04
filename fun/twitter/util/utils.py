import pandas as pd
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import scipy.stats as stats
import numpy as np


def augmented_dickey_fuller_statistics(
    coin, feature_name, time_series, diff_order, _diff
):
    """
    This function recursively applies adfuller on the time-series if p-value is less than 0.05, hence rejecting the below null hypothesis.
    
    Null hypothesis: Unit root is not detected (stationary time-series)
    
    Args:
        coin: The cryptocurrency the time-series belongs to
        feature_name: The name of the time-series
        time_series: The time-series to be test for stationary
        diff_order: The number of time the time-series has been differenced
        _diff: Dataframe containing all the differenced iteration of the time-series
        
    Returns:
        _diff: All the differenced iteration of the time-series 
        time_series: The final-series which is stationary.
    """

    global full_diff_df
    result = adfuller(time_series)
    if result[1] < 0.05:
        return _diff, time_series
    else:
        print(
            coin,
            feature_name,
            "p-value: %f" % result[1],
            "There is unit root (Cannot reject null hypothesis) - Repeat differencing",
        )

        diff_order += 1
        differencing = time_series.diff()

        diff_df = differencing.reset_index()
        diff_df["order"] = diff_order
        diff_df.set_index(["coin_symbol", "date", "order"], inplace=True)
        axis = 1 if feature_name in diff_df.columns else 0
        _diff = pd.concat([_diff, diff_df], axis=axis, join="outer")

        return augmented_dickey_fuller_statistics(
            coin, feature_name, differencing.dropna(), diff_order, _diff
        )


def transform_gc_date(
    coin, gc_test_result, c, r, maxlag, grangercausalitytests_df, verbose
):
    """
    This function transform the Granger Causality test results into columns of vectors for loading into atoti.
    
    Args:
        coin: The cryptocurrency the time-series belongs to
        gc_test_result: The test results of the grangercausalitytest
        c: The name of the feature that was tested to see if it Granger caused r
        r: The name of the feature that was tested to see if it is Granger caused by c
        maxlag: number of lags applied for the grangercausalitytest
        verbose: print debug statement if True
        
    Returns:
        Dataframe containing the Grangercausalitytest results transformed into vectors for each test:
        - ssr_ftest
        - ssr_chi2test
        - lrtest
        - params_ftest
    """
    for test in ["ssr_ftest", "ssr_chi2test", "lrtest", "params_ftest"]:
        result = {"coin_symbol": coin, "x": c, "y": r, "Test name": test}

        p_values = [round(gc_test_result[i + 1][0][test][1], 4) for i in range(maxlag)]

        # we store the p-values for each test and each lag
        result["p-value"] = ";".join(map(str, p_values))

        f_chi2 = [round(gc_test_result[i + 1][0][test][0], 4) for i in range(maxlag)]

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
    """
    This function prints the criteria for autocorrelation with Durbin watson
    """
    if value < 1.5:
        print("Positive correlation detected")
    elif value > 2.5:
        print("Negative correlation detected")
    else:
        print("No correlation detected")


def adjust(val, length=6):
    """
    This function left align the numerical value for printing purpose 
    """
    return str(val).ljust(length)


def forecast_accuracy(forecast, actual):
    """
    This function computes the statistical measures of accuracy of the forecast.
    
    Args:
        forecast: forecasted results
        actual: actual values
        
    Returns:
        - mape: mean absolute percentage error (the better the prediction, the lower the value)
        - me: mean error
        - mae: mean absolute error
        - rmse: root mean squared error
        - corr: correlation
        - minmax: min max accuracy (the better the prediction, the higher the value - 1 for perfect model)       
    """
    mape = np.mean(np.abs(forecast - actual) / np.abs(actual))  # MAPE
    me = np.mean(forecast - actual)  # ME
    mae = np.mean(np.abs(forecast - actual))  # MAE
    mpe = np.mean((forecast - actual) / actual)  # MPE
    rmse = np.mean((forecast - actual) ** 2) ** 0.5  # RMSE
    corr = np.corrcoef(forecast, actual)[0, 1]  # corr
    mins = np.amin(np.hstack([forecast[:, None], actual[:, None]]), axis=1)
    maxs = np.amax(np.hstack([forecast[:, None], actual[:, None]]), axis=1)
    minmax = 1 - np.mean(mins / maxs)  # minmax
    return {
        "mape": mape,
        "me": me,
        "mae": mae,
        "mpe": mpe,
        "rmse": rmse,
        "corr": corr,
        "minmax": minmax,
    }


def var_forecast(coin, data_stats, train_data, actual_df, nobs, verbose=False):
    """
    This function performs the following:
        - forecast the time-series using VAR 
        - durbin watson testing on the residual from the model
        - obtain normaltest, kurtosis and skewness of the residual from the model
        - compute the forecast accuracy
    
    The number of days forecast is the minimum value between the lag order and the nobs.
        
    Args:
        coin: The cryptocurrency the time-series belongs to
        data_stats: The data_stats dataframe for storing the durbin_watson, norm_stat, norm_p, kurtosis and skewness value
        train_data: Train data containing the features for VAR forecast
        actual_df: The actual value to be compared against the forecasted results
        nobs: Number of observations to forecast
        verbose: To print the debugging statements
        
    Returns:
        fitted_df: Dataframe containing residual of the features
        data_stats: Dataframe containing durbin_watson, norm_stat, norm_p, kurtosis and skewness value
        accuracy_prod: measures of accuracy for the forecast
        pred_df: predicted results
    """
    mod = VAR(train_data, freq="D")

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

        # get the residual values
        metric = res.resid[col]
        fitted_df[f"{col} residual"] = metric
        stat, p = stats.normaltest(metric)
        kurtosis = stats.kurtosis(metric)
        skewness = stats.skew(metric)

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
        # take the minimal forecast between the lag order and the number of observations required
        forecast_steps = lag_order if lag_order < nobs else nobs
        pred = res.forecast(y=input_data, steps=forecast_steps)

        # we generate index from the last date for a period equivalent to the size of the forecast
        last_date = train_data.tail(1).index.get_level_values("date").to_pydatetime()[0]
        date_indices = pd.date_range(
            start=last_date, periods=(forecast_steps + 1), closed="right"
        )
        pred_df = pd.DataFrame(
            pred, index=date_indices, columns=train_data.columns,
        ).reset_index()

        accuracy_prod = forecast_accuracy(
            pred_df["Returns"].values, actual_df["Returns"][:forecast_steps]
        )
        accuracy_prod = pd.DataFrame(accuracy_prod, index=[coin])
        accuracy_prod["lag_order"] = lag_order
        accuracy_prod["Observations"] = forecast_steps

        if verbose:
            for k, v in accuracy_prod.items():
                print(adjust(k), ": ", v)

        pred_df["Subset"] = "Test"
        fitted_df["Subset"] = "Train"

        return (
            fitted_df.drop(columns=train_data.columns).reset_index(),
            data_stats.loc[~data_stats["norm_stat"].isnull()],
            accuracy_prod,
            pred_df.rename(columns={"index": "date"}),
        )
