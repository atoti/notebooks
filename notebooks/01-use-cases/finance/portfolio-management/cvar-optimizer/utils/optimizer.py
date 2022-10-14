# https://bjerring.github.io/equity/2019/11/04/Portfolio-Optimization-using-CVaR.html
#%% packages

import pulp
import pandas as pd
import numpy as np
from pandas_datareader import data


#%% functions


def PortfolioRiskTarget(
    mu, scen, CVaR_target=1, lamb=1, max_weight=1, min_weight=None, cvar_alpha=0.05
):

    """This function finds the optimal enhanced index portfolio according to some benchmark. The portfolio corresponds to the tangency portfolio where risk is evaluated according to the CVaR of the tracking error. The model is formulated using fractional programming.

    Parameters
    ----------
    mu : pandas.Series with float values
        asset point forecast
    scen : pandas.DataFrame with float values
        Asset scenarios
    max_weight : float
        Maximum allowed weight
    cvar_alpha : float
        Alpha value used to evaluate Value-at-Risk one

    Returns
    -------
    float
        Asset weights in an optimal portfolio

    """

    # define index
    i_idx = mu.index
    j_idx = scen.index

    # number of scenarios
    N = scen.shape[0]

    # define variables
    x = pulp.LpVariable.dicts("x", ((i) for i in i_idx), lowBound=0, cat="Continuous")

    # loss deviation
    VarDev = pulp.LpVariable.dicts(
        "VarDev", ((t) for t in j_idx), lowBound=0, cat="Continuous"
    )

    # value at risk
    VaR = pulp.LpVariable("VaR", lowBound=0, cat="Continuous")
    CVaR = pulp.LpVariable("CVaR", lowBound=0, cat="Continuous")

    # binary variable connected to cardinality constraints
    b_z = pulp.LpVariable.dicts("b_z", ((i) for i in i_idx), cat="Binary")

    #####################################
    ## define model
    model = pulp.LpProblem("Mean-CVaR_Optimization", pulp.LpMaximize)

    #####################################
    ## Objective Function

    model += lamb * (pulp.lpSum([mu[i] * x[i] for i in i_idx])) - (1 - lamb) * CVaR

    #####################################
    # constraint

    # calculate CVaR
    for t in j_idx:
        model += -pulp.lpSum([scen.loc[t, i] * x[i] for i in i_idx]) - VaR <= VarDev[t]

    model += VaR + 1 / (N * cvar_alpha) * pulp.lpSum([VarDev[t] for t in j_idx]) == CVaR

    model += CVaR <= CVaR_target

    ### price*number of products cannot exceed budget
    model += pulp.lpSum([x[i] for i in i_idx]) == 1

    ### Concentration limits
    # set max limits so it cannot not be larger than a fixed value
    ###
    for i in i_idx:
        model += x[i] <= max_weight

    ### Add minimum weight constraint, either zero or atleast minimum weight
    if min_weight is not None:

        for i in i_idx:
            model += x[i] >= min_weight * b_z[i]
            model += x[i] <= b_z[i]

    # solve model
    model.solve()

    # print an error if the model is not optimal
    if pulp.LpStatus[model.status] != "Optimal":
        print(
            "Whoops! There is an error! The model has error status:"
            + pulp.LpStatus[model.status]
        )

    # Get positions
    if pulp.LpStatus[model.status] == "Optimal":

        # print variables
        var_model = dict()
        for variable in model.variables():
            var_model[variable.name] = variable.varValue

        # solution with variable names
        var_model = pd.Series(var_model, index=var_model.keys())

        long_pos = [i for i in var_model.keys() if i.startswith("x")]

        # total portfolio with negative values as short positions
        port_total = pd.Series(
            var_model[long_pos].values, index=[t[2:] for t in var_model[long_pos].index]
        )

        opt_port = port_total

    # set flooting data points to zero and normalize
    opt_port[opt_port < 0.000001] = 0
    opt_port = opt_port / sum(opt_port)

    # return portfolio, CVaR, and alpha
    return opt_port  # , var_model["CVaR"], (sum(np.asarray(mu) * np.asarray(port_total)) - mu_b).values[0] #(sum(mu * port_total) - mu_b)


# Frontier_port = PortfolioLambda(mu,scen,max_weight=1,min_weight=None,cvar_alpha=cvar_alpha)


def PortfolioLambda(
    mu, mu_b, scen, scen_b, max_weight=1, min_weight=None, cvar_alpha=0.05, ft_points=15
):

    # asset names
    assets = mu.index

    # column names
    col_names = mu.index.values.tolist()
    col_names.extend(["Mu", "CVaR", "STAR"])
    # number of frontier points

    # store portfolios
    portfolio_ft = pd.DataFrame(columns=col_names, index=list(range(ft_points)))

    # maximum risk portfolio
    lamb = 0.99999
    max_risk_port, max_risk_CVaR, max_risk_mu = PortfolioRiskTarget(
        mu=mu,
        scen=scen,
        CVaR_target=100,
        lamb=lamb,
        max_weight=max_weight,
        min_weight=min_weight,
        cvar_alpha=cvar_alpha,
    )
    print(ft_points - 1)
    print(f"assets: {assets}")
    print(f"max_risk_port: {max_risk_port}")
    portfolio_ft.loc[ft_points - 1, assets] = max_risk_port
    # portfolio_ft.loc[ft_points-1,"Mu"] = max_risk_mu
    # portfolio_ft.loc[ft_points-1,"CVaR"] = max_risk_CVaR
    # portfolio_ft.loc[ft_points-1,"STAR"] = max_risk_mu/max_risk_CVaR # return to risk ratio (Sharpe Ratio)

    # minimum risk portfolio
    lamb = 0.00001
    min_risk_port, min_risk_CVaR, min_risk_mu = PortfolioRiskTarget(
        mu=mu,
        scen=scen,
        CVaR_target=100,
        lamb=lamb,
        max_weight=max_weight,
        min_weight=min_weight,
        cvar_alpha=cvar_alpha,
    )
    portfolio_ft.loc[0, assets] = min_risk_port
    # portfolio_ft.loc[0,"Mu"] = min_risk_mu
    # portfolio_ft.loc[0,"CVaR"] = min_risk_CVaR
    # portfolio_ft.loc[0,"STAR"] = min_risk_mu/min_risk_CVaR

    # CVaR step size
    step_size = (max_risk_CVaR - min_risk_CVaR) / ft_points  # CVaR step size

    # calculate all frontier portfolios
    for i in range(1, ft_points - 1):
        CVaR_target = min_risk_CVaR + step_size * i
        i_risk_port, i_risk_CVaR, i_risk_mu = PortfolioRiskTarget(
            mu=mu,
            scen=scen,
            CVaR_target=CVaR_target,
            lamb=1,
            max_weight=max_weight,
            min_weight=min_weight,
            cvar_alpha=cvar_alpha,
        )
        portfolio_ft.loc[i, assets] = i_risk_port

    return portfolio_ft
