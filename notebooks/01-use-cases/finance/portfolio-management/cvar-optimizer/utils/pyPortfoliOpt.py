from pypfopt import (
    EfficientFrontier,
    EfficientCVaR,
    expected_returns,
    risk_models,
    CLA,
    objective_functions,
)
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import time
import pandas as pd
import copy
import numpy as np
from pypfopt import HRPOpt

# https://github.com/robertmartin8/PyPortfolioOpt/blob/master/cookbook/3-Advanced-Mean-Variance-Optimisation.ipynb
# https://github.com/robertmartin8/PyPortfolioOpt/blob/master/examples.py
# Deviation Risk Parity objective from Kolm et al (2014)
def deviation_risk_parity(w, cov_matrix):
    diff = w * np.dot(cov_matrix, w) - (w * np.dot(cov_matrix, w)).reshape(-1, 1)
    return (diff**2).sum().sum()


def get_optimised_weight(df_price, df_ini_weights, portfolio_name=None):
    """
    This function returns the optimized weights of the given portfolio based on the following algorithms:
    - Minimum CVaR (expected shortfall) using Efficient Frontier
    - Maximum Sharpe Ratio using critical line algorithm
    - Minimum volatility based on the initial weights from the portfolio using critical line algorithm
    - hierarchical risk parity portfolio allocation using hierarchical clustering model

    Args:
        df_price: A dataframe containing historical pricing of stocks in the portfolio
        df_ini_weights: A dataframe containing the initial weights allocated to the stocks in the portfolio
        portfolio_name: The name assigned to the portfolio

    Returns:
        The optimized weights return from each algorithm as follows:
        - min_cvar_weights,
        - max_sharpe_weights,
        - min_vol_weights,
        - hrpOpt_weights

    """

    # structured data to the required format
    df_price.reset_index(inplace=True)
    df_price = df_price.pivot(
        index="Historical Dates", columns="Symbols", values="Daily Price"
    )

    iteration = time.strftime("%Y%m%d_%X")
    # use optimiser to compute the metrics
    # Capital Asset Pricing Model - asset returns are equal to market returns plus a eta term encoding the relative risk of the asset.
    # more stable than the default mean return
    mu = expected_returns.capm_return(df_price)
    S = risk_models.semicovariance(df_price)

    print("---------------------------------------------------------")
    min_cvar_weights = added_info(
        portfolio_name, "min_cvar", get_min_cvar(mu, S), iteration
    )
    print("---------------------------------------------------------")
    max_sharpe_weights = added_info(
        portfolio_name, "max_sharpe", get_max_sharpe(mu, S), iteration
    )
    print("---------------------------------------------------------")
    min_vol_weights = added_info(
        portfolio_name,
        "min_volatility",
        get_min_volatility(mu, S, df_ini_weights),
        iteration,
    )
    print("---------------------------------------------------------")
    hrpOpt_weights = added_info(
        portfolio_name, "hrpOpt", get_hrpOpt(df_price), iteration
    )
    print("---------------------------------------------------------")

    # Alternative optimization methods
    # uncomment as required
    # print("---------------------------------------------------------")
    # nonconvex_weights = added_info(portfolio_name, "nonconvex", get_nonconvex(mu, S), iteration)
    # print("---------------------------------------------------------")
    # cla_weights = added_info(portfolio_name, "CLA", get_cla(mu, S), iteration)

    return min_cvar_weights, max_sharpe_weights, min_vol_weights, hrpOpt_weights


# def get_min_cvar(df_price):
def get_min_cvar(mu, S):
    print("Computing maximum return with")

    ef_cvar = EfficientCVaR(mu, S)
    cvar_weights = ef_cvar.min_cvar()
    cleaned_weights = ef_cvar.clean_weights()
    ef_cvar.portfolio_performance(verbose=True)

    return cleaned_weights


def get_max_sharpe(mu, S):
    print("Computing max sharpe")
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    ef.portfolio_performance(verbose=True)

    return cleaned_weights


def get_nonconvex(mu, S):
    # nonconvex objective
    print("Computing non-convex objective")
    ef = EfficientFrontier(mu, S)
    ef.min_volatility()
    weights = ef.nonconvex_objective(deviation_risk_parity, ef.cov_matrix)
    clean_weights = ef.clean_weights()
    ef.portfolio_performance(verbose=True)

    return clean_weights


def get_hrpOpt(df):
    print("Constructs a hierarchical risk parity portfolio")
    returns = df.pct_change().dropna()
    hrp = HRPOpt(returns)
    weights = hrp.optimize()
    hrp.portfolio_performance(verbose=True)

    return weights


def get_cla(mu, S):
    print("Critical Line Algorithm")
    cla = CLA(mu, S)
    cla.max_sharpe()
    weights = cla.clean_weights()
    cla.portfolio_performance(verbose=True)

    return weights


def get_min_volatility(mu, S, initial_weights):
    print("Compute minimum volatility with k=0.01")
    ef = EfficientFrontier(mu, S)

    ef.add_objective(
        objective_functions.transaction_cost, w_prev=initial_weights, k=0.01
    )
    # reduce number of zero weights
    ef.add_objective(objective_functions.L2_reg)
    ef.min_volatility()
    weights = ef.clean_weights()
    ef.portfolio_performance(verbose=True)

    return weights


def added_info(portfolio_name, opt_type, clean_weights, iteration):
    weights_df = (
        pd.DataFrame.from_dict(clean_weights, orient="index", columns=["Weights"])
        .rename_axis("Symbols")
        .reset_index()
    )

    weights_df["Portfolio"] = portfolio_name
    weights_df["Iteration"] = iteration
    weights_df["Opt Method"] = opt_type

    return weights_df
