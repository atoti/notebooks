from utils import pyPortfoliOpt as optimizer


class Helper:
    def __init__(self, session):
        self.session = session
        self.cube = session.cubes["Portfolio optimization"]

    def query_and_optimize(self, selected_port, selected_method, selected_iteration):
        l, m = self.cube.levels, self.cube.measures
        portfolio_tbl = self.session.tables["Portfolios Allocation"]

        df_historical_price = self.cube.query(
            m["Daily Price"],
            levels=[
                l["Historical Dates"],
                l[("Portfolios Allocation", "Symbols", "Symbols")],
            ],
            filter=(
                l[("Portfolios Allocation", "Portfolio", "Portfolio")] == selected_port
            ),
        )

        initial_weights = self.cube.query(
            m["Weights.SUM"],
            levels=[l[("Portfolios Allocation", "Symbols", "Symbols")]],
            filter=(
                l[("Portfolios Allocation", "Portfolio", "Portfolio")] == selected_port
            )
            & (l["Opt Method"] == selected_method)
            & (l["Iteration"] == selected_iteration),
        )
        initial_weights.reset_index(inplace=True)
        weight_list = initial_weights["Weights.SUM"].to_list()

        print(f"Start optimization...")
        (
            min_cvar_weights,
            max_sharpe_weights,
            min_vol_weights,
            hrpOpt_weights,
        ) = optimizer.get_optimised_weight(
            df_historical_price, weight_list, portfolio_name=selected_port
        )

        print(f"Loading optimization into atoti...")
        portfolio_tbl.load_pandas(min_cvar_weights)
        portfolio_tbl.load_pandas(max_sharpe_weights)
        portfolio_tbl.load_pandas(min_vol_weights)
        portfolio_tbl.load_pandas(hrpOpt_weights)

        print(f"Optimization loaded into atoti!")

    def get_opt_mtd(self, portfolio):
        l, m = self.cube.levels, self.cube.measures

        opt_mtd = ["-|Base"]
        if portfolio != None:
            opt_mtd_df = self.cube.query(
                m["contributors.COUNT"],
                levels=[l["Iteration"], l["Opt Method"]],
                filter=(
                    l[("Portfolios Allocation", "Portfolio", "Portfolio")] == portfolio
                ),
            )
            opt_mtd = opt_mtd_df.index.map("|".join).to_list()

        return opt_mtd
