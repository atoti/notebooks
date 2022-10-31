from pypfopt import (
    EfficientFrontier,
    EfficientCVaR,
    expected_returns,
    objective_functions,
    risk_models,
)
import pandas as pd
import cvxpy as cp


class Optimizer:
    def init_model(self, df_price):
        mu = expected_returns.mean_historical_return(df_price)
        S = risk_models.exp_cov(df_price)
        ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.25))

        return ef

    def basic_min_volatility(self, df_price):
        ef = self.init_model(df_price)
        ef.min_volatility()
        return_weights = ef.clean_weights()

        ef.portfolio_performance(verbose=True)

        weights_df = (
            pd.DataFrame.from_dict(return_weights, orient="index", columns=["Weights"])
            .rename_axis("Tickers")
            .reset_index()
        )

        return weights_df

    def basic_max_sharpe(self, df_price):
        ef = self.init_model(df_price)
        ef.max_sharpe()
        return_weights = ef.clean_weights()

        ef.portfolio_performance(verbose=True)

        weights_df = (
            pd.DataFrame.from_dict(return_weights, orient="index", columns=["Weights"])
            .rename_axis("Tickers")
            .reset_index()
        )

        return weights_df

    def exec_optimization(
        self,
        df_price,
        opt_target,
        sector_mapper,
        sector_upper,
        sector_lower,
        ticker_upper,
        ticker_lower,
        target_return=None,
    ):

        print("=====================================================")
        print(f"sector_mapper: {sector_mapper}")
        print(f"sector_upper: {sector_upper}")
        print(f"sector_lower: {sector_lower}")
        print(f"ticker_upper: {ticker_upper}")
        print(f"ticker_lower: {ticker_lower}")
        print("=====================================================")

        mu = expected_returns.mean_historical_return(df_price)
        S = risk_models.CovarianceShrinkage(
            df_price
        ).ledoit_wolf()  
        
        ef = (
            EfficientFrontier(mu, S, weight_bounds=(0, 0.25))
            if opt_target == "Target returns"
            else EfficientCVaR(mu, S, weight_bounds=(0, 0.25))
        )

        if len(sector_mapper) > 0:
            ef.add_sector_constraints(sector_mapper, sector_lower, sector_upper)

        if len(ticker_upper) > 0:
            for key, value in ticker_upper.items():
                index = ef.tickers.index(key)
                ef.add_constraint(lambda w: w[index] <= value)

        if len(ticker_lower) > 0:
            for key, value in ticker_lower.items():
                index = ef.tickers.index(key)
                ef.add_constraint(lambda w: w[index] >= value)

        if opt_target == "Minimize CVaR":
            ef.min_cvar()
        elif opt_target == "Target returns":
            print("Set target return: ", target_return)
            ef.efficient_return(target_return)

        return_weights = ef.clean_weights()
        ef.portfolio_performance(verbose=True)

        weights_df = (
            pd.DataFrame.from_dict(return_weights, orient="index", columns=["Weights"])
            .rename_axis("Tickers")
            .reset_index()
        )

        return weights_df
