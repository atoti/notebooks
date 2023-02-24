# Import some required packages
#############################################################################################################################
import os, sys
from time import sleep
from tqdm import tqdm

import pandas as pd, numpy as np, random, re, pickle, multiprocessing
from natsort import natsorted
from collections import Counter

from sklearn.utils.validation import check_consistent_length, check_array
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import r2_score, explained_variance_score, mean_squared_error

from pyopls import OPLS

from tsfresh import extract_features, select_features
from tsfresh.utilities.dataframe_functions import (
    impute,
    make_forecasting_frame,
    roll_time_series,
    restrict_input_to_index,
)
from tsfresh.feature_extraction import (
    ComprehensiveFCParameters,
    EfficientFCParameters,
    MinimalFCParameters,
    settings,
)

import pickle

############################################################################################################################


# Set the number of cpus to use for parallel computing
num_cpus = multiprocessing.cpu_count() - 2


# Define the helper functions


def create_forecasting_frame(dataframe, col, max_timeshift, rolling_direction):
    date_df, _ = make_forecasting_frame(
        dataframe["Date"],
        kind="Date",
        max_timeshift=max_timeshift,
        rolling_direction=rolling_direction,
    )
    value_df, y = make_forecasting_frame(
        dataframe[col],
        kind=col,
        max_timeshift=max_timeshift,
        rolling_direction=rolling_direction,
    )

    X = pd.merge(value_df, date_df, how="inner", on=["id", "time"])
    X = X.rename(
        columns={"value_x": "asset_value", "value_y": "date", "kind_x": "asset_code"}
    )
    X = X[["id", "time", "asset_value", "date", "asset_code"]].reset_index(drop=True)

    y = pd.DataFrame(y).reset_index()
    y = y.rename(columns={"index": "id", "value": "target"}).reset_index(drop=True)

    ######################################################################################################################################
    # OPTIONAL: THIS PART HAS BEEN ARBIRTRAILY ADDED TO FIX ISSUES WITH TSFRESH 0.19.0 FEATURES EXTRACTION IN OUR PROJECT.

    # Here we get rid of the ids appearing in only one row in the rolled datasets.
    # In fact, it seems that the version of the tsfresh library we are using in this project (latest version to this day: 0.19.0)
    # does not allow fetures extarction for ids with a unique row in the rolled datasets.
    # So we exclude such ids from the rolled datasets before performing features extraction.
    # Note that this is our choice, and you are free to chose another way to proceed.

    ids_counts = Counter(X["id"])
    ids_included = [idx for idx, count in ids_counts.items() if count > 1]
    X = restrict_input_to_index(X, "id", ids_included)
    y = restrict_input_to_index(y, "id", ids_included)
    ######################################################################################################################################

    return X, y


def update_test_data(test_data_path):
    """This function updates the test dataset according to the restriction of the index in the function create_forecasting_frame().
    This allows to have all the datasets with the same index: test data, features extration tables, predictions tables, etc.

    Argument:
        test_data_path - the complete path to the test data

    Return: the updated test dataset.
    """

    test_data = pd.read_csv(test_data_path)

    # We choose the maximum shift = 10 and the rolling direction = 1 arbitrarily
    # this is not very importante for what we're trying to do here
    max_timeshift = 10
    rolling_direction = 1
    col = test_data.columns[
        1
    ]  # we choose the columns corresponding to the first asset arbitrarily

    date_df, _ = make_forecasting_frame(
        test_data["Date"],
        kind="Date",
        max_timeshift=max_timeshift,
        rolling_direction=rolling_direction,
    )
    value_df, y = make_forecasting_frame(
        test_data[col],
        kind=col,
        max_timeshift=max_timeshift,
        rolling_direction=rolling_direction,
    )

    X = pd.merge(value_df, date_df, how="inner", on=["id", "time"])
    X = X.rename(
        columns={"value_x": "asset_value", "value_y": "date", "kind_x": "asset_code"}
    )
    X = X[["id", "time", "asset_value", "date", "asset_code"]].reset_index(drop=True)

    ids_counts = Counter(X["id"])
    ids_included = [idx for idx, count in ids_counts.items() if count > 1]

    if len(ids_included) < len(X):
        dates_included = np.unique(X["date"].values)[1:]

    test_data = restrict_input_to_index(test_data, "Date", dates_included)

    # save the updated dataset
    # test_data.to_csv(test_data_path, index=False)

    return test_data


def create_and_save_dataset(forecasting_frame_tuple, path, horizon, split):
    X, y = forecasting_frame_tuple
    y_shifted = y.copy()
    y_shifted["target"] = y_shifted["target"].shift(1 - horizon)
    dataset_name = np.unique(X["asset_code"])[0]

    if horizon > 1:
        horizon = str(horizon) + "-days-horizon-"
    else:
        horizon = str(horizon) + "-day-horizon-"

    filename = os.path.join(
        path, "rolled-dataset-" + horizon + "-" + dataset_name + "-" + split + ".pkl"
    )

    with open(filename, "wb") as fOut:
        pickle.dump({"X": X, "y": y_shifted}, fOut, protocol=pickle.HIGHEST_PROTOCOL)


def generate_features_dataframes(input_path, output_path):
    # list all the rolled dataset
    rolled_datasets_train = natsorted(
        [d for d in os.listdir(input_path) if "train" in d]
    )
    rolled_datasets_test = natsorted([d for d in os.listdir(input_path) if "test" in d])
    sanity_check = True
    error_tracker = []

    # loop over the rolled datasets
    # to extract the features

    print("Starting features extraction...\n\n")
    for i in range(len(rolled_datasets_train)):
        # load the data
        train = rolled_datasets_train[i]
        test = rolled_datasets_test[i]

        with open(os.path.join(input_path, train), "rb") as fIn:
            stored_data = pickle.load(fIn)
            X_train = stored_data["X"].reset_index(drop=True)
            y_train = stored_data["y"].reset_index(drop=True)

        with open(os.path.join(input_path, test), "rb") as fIn:
            stored_data = pickle.load(fIn)
            X_test = stored_data["X"].reset_index(drop=True)
            y_test = stored_data["y"].reset_index(drop=True)

        # extract the dates
        ids_train = list(np.unique(X_train.id))
        dates_train = []

        for idx in ids_train:
            temp = X_train[X_train["id"] == idx].reset_index(drop=True)
            dates_train.append(temp.iloc[len(temp) - 1, 3])
        dates_train = pd.DataFrame(dates_train, columns=["date"])

        ids_test = list(np.unique(X_test.id))
        dates_test = []

        for idx in ids_test:
            temp = X_test[X_test["id"] == idx].reset_index(drop=True)
            dates_test.append(temp.iloc[len(temp) - 1, 3])
        dates_test = pd.DataFrame(dates_test, columns=["date"])

        # extract the features
        cols = ["id", "time", "asset_value"]
        features_train = extract_features(
            X_train[cols],
            default_fc_parameters=ComprehensiveFCParameters(),  # we could use also: MinimalFCParameters(), EfficientFCParameters()
            column_id="id",
            column_sort="time",
            impute_function=impute,
            n_jobs=num_cpus,
        )

        features_test = extract_features(
            X_test[cols],
            default_fc_parameters=ComprehensiveFCParameters(),  # we could use also: MinimalFCParameters(), EfficientFCParameters()
            column_id="id",
            column_sort="time",
            impute_function=impute,
            n_jobs=num_cpus,
        )

        # remove the rows whose target values are NaNs
        remove_indices_train = y_train["target"].index[
            y_train["target"].apply(np.isnan)
        ]
        indices_train = [
            idx for idx in y_train.index if idx not in remove_indices_train
        ]

        remove_indices_test = y_test["target"].index[y_test["target"].apply(np.isnan)]
        indices_test = [idx for idx in y_test.index if idx not in remove_indices_test]

        features_train = features_train.reset_index(drop=True)
        features_train = features_train.iloc[indices_train]
        y_train = y_train.iloc[indices_train]
        dates_train = dates_train.iloc[indices_train]

        features_test = features_test.reset_index(drop=True)
        features_test = features_test.iloc[indices_test]
        y_test = y_test.iloc[indices_test]
        dates_test = dates_test.iloc[indices_test]

        # normalize the features
        cols = features_train.columns
        scaler = StandardScaler()
        features_train = pd.DataFrame(
            scaler.fit_transform(features_train), columns=cols
        )
        features_test = pd.DataFrame(scaler.transform(features_test), columns=cols)

        # add the dates
        features_train["day"] = pd.to_datetime(dates_train["date"]).dt.day
        features_train["week"] = pd.to_datetime(dates_train["date"]).dt.week
        features_train["month"] = pd.to_datetime(dates_train["date"]).dt.month

        features_test["day"] = pd.to_datetime(dates_test["date"]).dt.day
        features_test["week"] = pd.to_datetime(dates_test["date"]).dt.week
        features_test["month"] = pd.to_datetime(dates_test["date"]).dt.month

        # filter the features
        features_selected_train = select_features(features_train, y_train.target)
        features_selected_test = features_test[features_selected_train.columns]

        # generate the final dataframe
        # containing the filtered features and the target
        df_train = features_selected_train.merge(
            y_train.target, left_index=True, right_index=True
        )
        df_test = features_selected_test.merge(
            y_test.target, left_index=True, right_index=True
        )

        # add dates index
        index_train = pd.Series(list(dates_train["date"]))
        df_train = df_train.set_index(index_train)

        index_test = pd.Series(list(dates_test["date"]))
        df_test = df_test.set_index(index_test)

        # export to csv and pickle
        filename_train = re.sub(
            ".pkl", ".csv", re.sub("rolled-dataset", "features", train)
        )
        filename_test = re.sub(
            ".pkl", ".csv", re.sub("rolled-dataset", "features", test)
        )
        filename_scaler = re.sub(
            "-train", "", re.sub("rolled-dataset", "scaler", train)
        )

        df_train.to_csv(os.path.join(output_path, filename_train))
        df_test.to_csv(os.path.join(output_path, filename_test))
        with open(os.path.join(output_path, filename_scaler), "wb") as fOut:
            pickle.dump(scaler, fOut, protocol=pickle.HIGHEST_PROTOCOL)

        # sanity check
        check = np.unique(df_test.columns == df_train.columns)
        if len(check) > 1 or not check[0]:
            sanity_check = False
            error_tracker.append((filename_test, filename_train))

    if sanity_check:
        print("\n\n...Features extraction completed, all the files are OK!!!\n\n")
    else:
        print("\n\n...The following pairs of files are not matching:")
        for el in error_tracker:
            print(el)
        print()


def build_models_and_results_summary(results_path, eval_metric="RMSE"):
    """
    Build and save the forecating models, and the result tables that summarize their performance.
    The results summary tables contain the results of the forecast of all the assets at different time horizons.

    Parameters:
        - results_path: The path to the results.
        - eval_metric: The evaluation metric considered to select the best performing model.
                     Should be one of: 'R2', 'RMSE', or 'MAPE'.

    Return:
        The tables containing all the results of the forecasting.
    """

    assert eval_metric in [
        "R2",
        "RMSE",
        "MAPE",
    ], "The evaluation metric must be 'R2', 'RMSE', or 'MAPE'."

    assets = [
        "AC.PA",
        "BNP.PA",
        "CAP.PA",
        "ENGI.PA",
        "G.MI",
        "RACE.MI",
        "SAN.PA",
        "TIT.MI",
    ]
    horizons = ["1-day-horizon--", "3-days-horizon--", "7-days-horizon--"]

    values = len(assets) * len(horizons)

    with tqdm(total=values, file=sys.stdout) as pbar:
        for horizon in horizons:
            for asset in assets:
                train = pd.read_csv(
                    os.path.join(
                        results_path,
                        "features",
                        "features-" + horizon + asset + "-train.csv",
                    ),
                    index_col=0,
                )
                test = pd.read_csv(
                    os.path.join(
                        results_path,
                        "features",
                        "features-" + horizon + asset + "-test.csv",
                    ),
                    index_col=0,
                )

                X_cols = [c for c in train.columns if c != "target"]
                y_col = "target"

                X_train = train[X_cols]
                y_train = train[y_col]

                X_test = test[X_cols]
                y_test = test[y_col]

                # Select the best models
                # using cross-validation

                # PLS
                pls = PLSRegression(1)

                y_pred_pls = cross_val_predict(pls, X_train, y_train, cv=10)
                r2_pls = r2_score(y_train, y_pred_pls)
                rmse_pls = mean_squared_error(y_train, y_pred_pls)
                mape_pls = mean_absolute_percentage_error(y_train, y_pred_pls)

                # OPLS
                opls = OPLS(20)
                Z = opls.fit_transform(X_train, y_train)

                y_pred_opls = cross_val_predict(pls, Z, y_train, cv=10)
                r2_opls = r2_score(y_train, y_pred_opls)
                rmse_opls = mean_squared_error(y_train, y_pred_opls)
                mape_opls = mean_absolute_percentage_error(y_train, y_pred_opls)

                ## Gradient Boosting
                gb_params = {
                    "learning_rate": 0.1,
                    "n_estimators": 10000,
                    "subsample": 0.9,
                    "max_depth": None,
                    "max_features": "auto",
                    "n_iter_no_change": 5,
                    "random_state": 42,
                }
                gb = GradientBoostingRegressor(**gb_params)

                y_pred_gb = cross_val_predict(gb, X_train, y_train, cv=10)
                r2_gb = r2_score(y_train, y_pred_gb)
                rmse_gb = mean_squared_error(y_train, y_pred_gb)
                mape_gb = mean_absolute_percentage_error(y_train, y_pred_gb)

                # Random Forest
                rf_params = {
                    "max_features": "auto",
                    "n_estimators": 300,
                    "bootstrap": True,
                    "oob_score": True,
                    "n_jobs": num_cpus,
                    "random_state": 42,
                }
                rf = RandomForestRegressor(**rf_params)

                y_pred_rf = cross_val_predict(rf, X_train, y_train, cv=10)
                r2_rf = r2_score(y_train, y_pred_rf)
                rmse_rf = mean_squared_error(y_train, y_pred_rf)
                mape_rf = mean_absolute_percentage_error(y_train, y_pred_rf)

                results_dic = {
                    "R2": {
                        "PLS": r2_pls,
                        "O-PLS": r2_opls,
                        "RF": r2_rf,
                        "GBoost": r2_gb,
                    },
                    "RMSE": {
                        "PLS": rmse_pls,
                        "O-PLS": rmse_opls,
                        "RF": rmse_rf,
                        "GBoost": rmse_gb,
                    },
                    "MAPE": {
                        "PLS": mape_pls,
                        "O-PLS": mape_opls,
                        "RF": mape_rf,
                        "GBoost": mape_gb,
                    },
                }

                models_perf = [
                    (model, perf) for model, perf in results_dic[eval_metric].items()
                ]

                if eval_metric in ["MAPE", "RMSE"]:
                    models_perf = sorted(models_perf, key=lambda x: x[1], reverse=False)
                elif eval_metric == "R2":
                    models_perf = sorted(models_perf, key=lambda x: x[1], reverse=True)

                best_model_name = models_perf[0][0]

                # Train it with all the training data
                # Make predictions on the test data
                # And compute some evaluation metrics

                pls = PLSRegression(1)
                gb = GradientBoostingRegressor(**gb_params)
                rf = RandomForestRegressor(**rf_params)
                model_name = None

                if best_model_name == "PLS":
                    model_name = "PLS"
                    best_model = pls.fit(X_train, y_train)
                    y_pred = best_model.predict(X_test)
                elif best_model_name == "O-PLS":
                    model_name = "O-PLS"
                    best_model = pls.fit(Z, y_train)
                    Z_test = opls.transform(X_test)
                    y_pred = best_model.predict(Z_test)
                elif best_model_name == "RF":
                    model_name = "Random-Forest"
                    best_model = rf.fit(X_train, y_train)
                    y_pred = best_model.predict(X_test)
                elif best_model_name == "GBoost":
                    model_name = "Gradient-Boosting"
                    best_model = gb.fit(X_train, y_train)
                    y_pred = best_model.predict(X_test)

                assert model_name != None, "Best Model was not identified!!!"

                r2 = r2_score(y_test, y_pred)
                rmse = mean_squared_error(y_test, y_pred)
                mape = mean_absolute_percentage_error(y_test, y_pred)

                # Serialize the models
                pickle_file = os.path.join(
                    results_path,
                    "models",
                    model_name + "-" + horizon + "-" + asset + ".pkl",
                )
                with open(pickle_file, "wb") as fOut:
                    pickle.dump(
                        {"model": best_model}, fOut, protocol=pickle.HIGHEST_PROTOCOL
                    )

                # Table with the predictions

                results = pd.DataFrame()
                results["y"] = y_test
                results["ŷ"] = y_pred
                results["Model Name"] = [model_name] * len(y_test)
                results["forecasting horizon in days"] = [horizon.split("-")[0]] * len(
                    y_test
                )
                results["Asset Code"] = [asset] * len(y_test)

                # Results summary table
                summary_table = pd.DataFrame(index=pd.Series(["Best Model"]))
                summary_table["R2"] = r2
                summary_table["RMSE"] = rmse
                summary_table["MAPE"] = mape
                summary_table["y_mean"] = np.mean(y_test)
                summary_table["y_std"] = np.std(y_test)
                summary_table["ŷ_mean"] = np.mean(y_pred)
                summary_table["ŷ_std"] = np.std(y_pred)
                summary_table["Model Name"] = model_name
                results["forecasting horizon in days"] = horizon.split("-")[0]
                summary_table["Asset Code"] = asset

                # save the tables
                results.to_csv(
                    os.path.join(
                        results_path,
                        "predictions",
                        model_name + "-predictions-" + horizon + asset + "-test.csv",
                    )
                )
                summary_table.to_csv(
                    os.path.join(
                        results_path,
                        "summary",
                        model_name + "-summary-" + horizon + asset + "-test.csv",
                    )
                )

                res = "predictions-" + horizon + asset + "-test.csv"
                pbar.write(f"processed: {res}")
                pbar.update(1)
                sleep(1)


def mean_absolute_percentage_error(
    y_true, y_pred, sample_weight=None, multioutput="uniform_average"
):
    """Mean absolute percentage error regression loss.
    Note here that we do not represent the output as a percentage in range
    [0, 100]. Instead, we represent it in range [0, 1/eps]. Read more in the
    :ref:`User Guide <mean_absolute_percentage_error>`.
    .. versionadded:: 0.24
    Parameters
    ----------
    y_true : array-like of shape (n_samples,) or (n_samples, n_outputs)
        Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,) or (n_samples, n_outputs)
        Estimated target values.
    sample_weight : array-like of shape (n_samples,), default=None
        Sample weights.
    multioutput : {'raw_values', 'uniform_average'} or array-like
        Defines aggregating of multiple output values.
        Array-like value defines weights used to average errors.
        If input is list then the shape must be (n_outputs,).
        'raw_values' :
            Returns a full set of errors in case of multioutput input.
        'uniform_average' :
            Errors of all outputs are averaged with uniform weight.
    Returns
    -------
    loss : float or ndarray of floats in the range [0, 1/eps]
        If multioutput is 'raw_values', then mean absolute percentage error
        is returned for each output separately.
        If multioutput is 'uniform_average' or an ndarray of weights, then the
        weighted average of all output errors is returned.
        MAPE output is non-negative floating point. The best value is 0.0.
        But note the fact that bad predictions can lead to arbitarily large
        MAPE values, especially if some y_true values are very close to zero.
        Note that we return a large value instead of `inf` when y_true is zero.
    Examples
    --------
    >>> from sklearn.metrics import mean_absolute_percentage_error
    >>> y_true = [3, -0.5, 2, 7]
    >>> y_pred = [2.5, 0.0, 2, 8]
    >>> mean_absolute_percentage_error(y_true, y_pred)
    0.3273...
    >>> y_true = [[0.5, 1], [-1, 1], [7, -6]]
    >>> y_pred = [[0, 2], [-1, 2], [8, -5]]
    >>> mean_absolute_percentage_error(y_true, y_pred)
    0.5515...
    >>> mean_absolute_percentage_error(y_true, y_pred, multioutput=[0.3, 0.7])
    0.6198...
    """
    y_type, y_true, y_pred, multioutput = _check_reg_targets(
        y_true, y_pred, multioutput
    )
    check_consistent_length(y_true, y_pred, sample_weight)
    epsilon = np.finfo(np.float64).eps
    mape = np.abs(y_pred - y_true) / np.maximum(np.abs(y_true), epsilon)
    output_errors = np.average(mape, weights=sample_weight, axis=0)
    if isinstance(multioutput, str):
        if multioutput == "raw_values":
            return output_errors
        elif multioutput == "uniform_average":
            # pass None as weights to np.average: uniform mean
            multioutput = None

    return np.average(output_errors, weights=multioutput)


def _check_reg_targets(y_true, y_pred, multioutput, dtype="numeric"):
    """Check that y_true and y_pred belong to the same regression task.
    Parameters
    ----------
    y_true : array-like
    y_pred : array-like
    multioutput : array-like or string in ['raw_values', uniform_average',
        'variance_weighted'] or None
        None is accepted due to backward compatibility of r2_score().
    Returns
    -------
    type_true : one of {'continuous', continuous-multioutput'}
        The type of the true target data, as output by
        'utils.multiclass.type_of_target'.
    y_true : array-like of shape (n_samples, n_outputs)
        Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples, n_outputs)
        Estimated target values.
    multioutput : array-like of shape (n_outputs) or string in ['raw_values',
        uniform_average', 'variance_weighted'] or None
        Custom output weights if ``multioutput`` is array-like or
        just the corresponding argument if ``multioutput`` is a
        correct keyword.
    dtype : str or list, default="numeric"
        the dtype argument passed to check_array.
    """
    check_consistent_length(y_true, y_pred)
    y_true = check_array(y_true, ensure_2d=False, dtype=dtype)
    y_pred = check_array(y_pred, ensure_2d=False, dtype=dtype)

    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))

    if y_pred.ndim == 1:
        y_pred = y_pred.reshape((-1, 1))

    if y_true.shape[1] != y_pred.shape[1]:
        raise ValueError(
            "y_true and y_pred have different number of output "
            "({0}!={1})".format(y_true.shape[1], y_pred.shape[1])
        )

    n_outputs = y_true.shape[1]
    allowed_multioutput_str = ("raw_values", "uniform_average", "variance_weighted")
    if isinstance(multioutput, str):
        if multioutput not in allowed_multioutput_str:
            raise ValueError(
                "Allowed 'multioutput' string values are {}. "
                "You provided multioutput={!r}".format(
                    allowed_multioutput_str, multioutput
                )
            )
    elif multioutput is not None:
        multioutput = check_array(multioutput, ensure_2d=False)
        if n_outputs == 1:
            raise ValueError("Custom weights are useful only in " "multi-output cases.")
        elif n_outputs != len(multioutput):
            raise ValueError(
                ("There must be equally many custom weights " "(%d) as outputs (%d).")
                % (len(multioutput), n_outputs)
            )
    y_type = "continuous" if n_outputs == 1 else "continuous-multioutput"

    return y_type, y_true, y_pred, multioutput


def truncate(num, digits):
    """
    Truncate num keeping only digits decimals.

    Parameters
    ----------
    num : a number
    digits : a number (of decimals)

    Returns
    -------
    The truncated number.
    """

    truncated_num = num

    try:
        sp = str(num).split(".")
        int_part = sp[0]
        dec_part = sp[1]

        if digits > len(dec_part):
            digits = len(dec_part)
        truncated_num = float(".".join([int_part, dec_part[:digits]]))
    except:
        pass

    return truncated_num
