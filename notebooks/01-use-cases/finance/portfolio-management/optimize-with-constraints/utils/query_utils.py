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
        weight_upper,
        weight_lower,
        limit_type="Ticker",
    ):

        scenario = "Ticker weight simulation"
        max_weight = "Max ticker weight"
        min_weight = "Min ticker weight"
        column_name = "Tickers"
        simulation_name = "Ticker weight simulation"

        if limit_type == "Sector":
            scenario = "Sector weight simulation"
            max_weight = "Max sector weight"
            min_weight = "Min sector weight"
            column_name = "GICS Sector"
            simulation_name = "Sector weight simulation"

        limits_df = pd.merge(
            pd.DataFrame(weight_upper.items(), columns=[column_name, max_weight]),
            pd.DataFrame(weight_lower.items(), columns=[column_name, min_weight]),
            how="outer",
            on=[column_name],
        )
        limits_df["Scenario"] = scenario
        limits_df["Portfolio"] = portfolio
        limits_df["Opt Method"] = opt_mtd

        limit_simulation = self.session.tables[simulation_name]
        # print(limit_simulation)

        limit_simulation.load_pandas(limits_df)

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
