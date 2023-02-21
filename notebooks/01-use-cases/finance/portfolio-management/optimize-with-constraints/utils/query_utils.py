import atoti as tt
import pandas as pd


class Query:
    def __init__(self, session):
        self.session = session
        self.cube = session.cubes["Portfolio optimization"]

        self.l = self.cube.levels
        self.m = self.cube.measures

    def get_portfolio(self):
        portfolio_df = self.cube.query(
            self.m["contributors.COUNT"],
            levels=[self.l["Portfolio"], self.l["Iteration"], self.l["Opt Method"]],
        )

        return portfolio_df.index.get_level_values(0).unique().to_list()

    def get_portfolio_details(self, _portfolio, _iteration=None):
        portfolio_dtl = self.cube.query(
            self.m["contributors.COUNT"],
            levels=[
                self.l["Portfolio"],
                self.l[("Portfolios Allocation", "Iteration", "Iteration")],
                self.l[("Portfolios Allocation", "Opt Method", "Opt Method")],
            ],
            filter=(self.l["Portfolio"] == _portfolio),
            mode="raw",
        )

        iteration_list = portfolio_dtl["Iteration"].unique().tolist()

        # get the opt method for the first default method
        iter_val = _iteration if _iteration != None else iteration_list[0]
        opt_mtd_list = portfolio_dtl[portfolio_dtl["Iteration"] == iter_val][
            "Opt Method"
        ].to_list()

        iteration_list.sort()
        opt_mtd_list.sort()

        return iteration_list, opt_mtd_list

    def get_weights(self, _portfolio, _iteration, _opt_mtd, weight_type):
        weights = {}
        portfolio_dtl = self.cube.query(
            self.m["contributors.COUNT"],
            self.m["Weights.SUM"],
            levels=[self.l[weight_type]],
            filter=(self.l["Portfolio"] == _portfolio)
            & (
                self.l[("Portfolios Allocation", "Iteration", "Iteration")]
                == _iteration
            )
            & (
                self.l[("Portfolios Allocation", "Opt Method", "Opt Method")]
                == _opt_mtd
            ),
        )

        portfolio_dtl = portfolio_dtl.reset_index()
        for row in portfolio_dtl.to_dict("records"):
            weights[row[weight_type]] = {
                "min": 0.0,
                "max": 1.0,
                "current": row["Weights.SUM"],
            }

        return weights

    def get_historical_pricing(self, portfolio, iteration, opt_mtd):
        df_historical_price = self.cube.query(
            self.m["Daily Price"],
            levels=[
                self.l["Historical Dates"],
                self.l["Tickers"],
            ],
            filter=(
                (self.l["Portfolio"] == portfolio)
                & (self.l["Iteration"] == iteration)
                & (self.l["Opt Method"] == opt_mtd)
            ),
        )

        df_historical_price.reset_index(inplace=True)
        df_price = df_historical_price.pivot(
            index="Historical Dates", columns="Tickers", values="Daily Price"
        )

        return df_price

    def get_sector_spread(self, portfolio, iteration, opt_mtd):
        sector_df = self.cube.query(
            self.m["contributors.COUNT"],
            levels=[self.l["GICS Sector"], self.l["Tickers"]],
            filter=(
                (self.l["Portfolio"] == portfolio)
                & (self.l["Iteration"] == iteration)
                & (self.l["Opt Method"] == opt_mtd)
            ),
        )

        return sector_df

    def load_weights(self, weights_df):
        portfolio_table = self.session.tables["Portfolios Allocation"]
        portfolio_table.load_pandas(weights_df)

    def load_limits(
        self,
        portfolio,
        # iteration,
        opt_mtd,
        sector_spread,
        sector_weight_upper,
        sector_weight_lower,
        ticker_weight_upper,
        ticker_weight_lower,
        target_returns,
        # limit_type="Ticker",
    ):
        lb_ticker_max_weight = "Max ticker weight"
        lb_ticker_min_weight = "Min ticker weight"
        lb_sector_max_weight = "Max sector weight"
        lb_sector_min_weight = "Min sector weight"
        lb_sector_column_name = "GICS Sector"
        lb_ticker_column_name = "Tickers"
        lb_simulation_name = "Weight simulation"

        sector_limits_df = pd.merge(
            pd.DataFrame(
                sector_weight_upper.items(),
                columns=[lb_sector_column_name, lb_sector_max_weight],
            ),
            pd.DataFrame(
                sector_weight_lower.items(),
                columns=[lb_sector_column_name, lb_sector_min_weight],
            ),
            how="outer",
            on=[lb_sector_column_name],
        )

        ticker_limits_df = pd.merge(
            pd.DataFrame(
                ticker_weight_upper.items(),
                columns=[lb_ticker_column_name, lb_ticker_max_weight],
            ),
            pd.DataFrame(
                ticker_weight_lower.items(),
                columns=[lb_ticker_column_name, lb_ticker_min_weight],
            ),
            how="outer",
            on=[lb_ticker_column_name],
        )

        # get sector for the ticker
        _ticker_df = pd.merge(
            ticker_limits_df, sector_spread, on=[lb_ticker_column_name], how="inner"
        )
        limits_df = pd.merge(
            sector_limits_df, _ticker_df, on=[lb_sector_column_name], how="outer"
        )

        limits_df["Scenario"] = lb_simulation_name
        limits_df["Portfolio"] = portfolio
        limits_df["Opt Method"] = opt_mtd
        limits_df["Target returns"] = target_returns

        limit_simulation = self.session.tables[lb_simulation_name]
        limit_simulation.load_pandas(limits_df[limit_simulation.columns])

    ###########################
    # For sector optimization
    ###########################

    def get_distinct_sectors(self):
        sector_df = self.cube.query(
            self.m["contributors.COUNT"], levels=[self.l["GICS Sector"]], mode="raw"
        )
        return sector_df["GICS Sector"].to_list()

    def get_historical_price_by_sector(self, sector):
        df_historical_price = self.cube.query(
            self.m["Daily Price"],
            levels=[
                self.l["Historical Dates"],
                self.l["Tickers"],
            ],
            filter=(self.l["GICS Sector"] == sector),
        )

        df_historical_price.reset_index(inplace=True)
        df_price = df_historical_price.pivot(
            index="Historical Dates", columns="Tickers", values="Daily Price"
        )

        return df_price
