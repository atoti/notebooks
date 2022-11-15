import functools
from utils import optimizer_utils as opt_utils
import ipywidgets as widgets
from IPython.display import display
import time
import pandas as pd


class Widgets:
    def __init__(self, query):

        self.optimizer = opt_utils.Optimizer()
        self.query = query
        portfolio = query.get_portfolio()

        self.init_constants()
        self.init_widgets(portfolio)

    def init_widgets(self, portfolio):
        self.min_sec_wid = widgets.Text(
            value="0.0", description="Min. total", disabled=True
        )
        self.max_sec_wid = widgets.Text(
            value="0.0", description="Max. total", disabled=True
        )
        self.min_sym_wid = widgets.Text(
            value="0.0", description="Min. total", disabled=True
        )
        self.max_sym_wid = widgets.Text(
            value="0.0", description="Max. total", disabled=True
        )

        # horizontal line
        self.hr = widgets.HTML(value="<hr/>")

        self.portfolio_dropdown = widgets.Dropdown(
            options=portfolio,
            value=None,
            description="Portfolio:",
            disabled=False,
        )

        self.iteration_dropdown = widgets.Dropdown(
            description="Iteration:",
            disabled=True,
        )

        self.opt_mtd_dropdown = widgets.Dropdown(
            description="Opt mtd:",
            disabled=True,
        )

        self.opt_target_radio = widgets.RadioButtons(
            options=["Minimize CVaR", "Target returns"],
            value="Minimize CVaR",
            layout={
                "width": "max-content",
                "display": "flex",
                "flex-direction": "row !important",
            },
            description="Objective (Not for basic optimization):",
            disabled=False,
        )

        self.target_returns = widgets.BoundedFloatText(
            max=1.0,
            step=0.01,
            disabled=True,
            layout=widgets.Layout(width="100px"),
        )

        self.wo_constraint_button = widgets.Button(
            description="Basic optimization",
            disabled=True,
            button_style="info",
            tooltip="Optimize portfolio without constraints",
            icon="gear",
        )
        self.sector_button = widgets.Button(
            description="Optimize sector",
            disabled=True,
            button_style="info",
            tooltip="Optimize portfolio without ticker limitation",
            icon="gear",
        )

        self.ticker_button = widgets.Button(
            description="Optimize tickers",
            disabled=True,
            button_style="info",
            tooltip="Optimize portfolio without sector limitation",
            icon="gear",
        )

        self.portfolio_button = widgets.Button(
            description="Optimize portfolio",
            disabled=True,
            button_style="info",
            tooltip="Optimize portfolio with sector and ticker limitations",
            icon="gear",
        )

        self.wo_constraint_button.on_click(self.optimize_basic)
        self.sector_button.on_click(self.submit_sector)
        self.ticker_button.on_click(self.submit_tickers)
        self.portfolio_button.on_click(self.submit_portfolio)

        self.tab_widget = widgets.Tab()
        self.tab_widget.disabled = True

        self.success_msg = widgets.HTML(value=None)
        self.warning_msg = widgets.HTML(value=None)

        self.styling = widgets.HTML(
            value="<style>.widget-radio-box {flex-direction: row !important;}.widget-radio-box label{margin:5px !important;width: 120px !important;}</style>"
        )

        self.portfolio_dropdown.observe(self.on_portfolio_change, names=["value"])
        self.iteration_dropdown.observe(self.on_iteration_change, names=["value"])
        self.opt_mtd_dropdown.observe(self.on_opt_change, names=["value"])
        self.opt_target_radio.observe(self.on_radio_change, names=["value"])

    def init_constants(self):
        self.SECTOR_TYPE = "Sector"
        self.TICK_TYPE = "Tickers"

    def get_final_weights(self, obj):
        # obtain the latest weights
        weights_lower = {}
        weights_upper = {}

        for child in obj:
            if isinstance(child.children[2], widgets.BoundedFloatText) & isinstance(
                child.children[3], widgets.BoundedFloatText
            ):
                if child.children[2].value > 0:
                    weights_lower[child.children[0].value] = child.children[2].value
                if child.children[3].value < 1:
                    weights_upper[child.children[0].value] = child.children[3].value

        return weights_lower, weights_upper  # , max_optional

    def load_basic_results(self, _portfolio, _iteration, _opt_mtd, weights_df):

        weights_df["Portfolio"] = _portfolio
        weights_df["Iteration"] = _iteration
        weights_df["Opt Method"] = _opt_mtd
        self.query.load_weights(weights_df)

    def optimize_basic(self, b):
        portfolio = self.portfolio_dropdown.value
        iteration = self.iteration_dropdown.value
        opt_mtd = self.opt_mtd_dropdown.value
        new_iteration = time.strftime("%Y%m%d_%X")

        historical_pricing = self.query.get_historical_pricing(
            portfolio, iteration, opt_mtd
        )

        weights_min_vol = self.optimizer.basic_min_volatility(historical_pricing)
        self.load_basic_results(
            portfolio, new_iteration, f"Min volatility_{new_iteration}", weights_min_vol
        )

        weights_max_sharpe = self.optimizer.basic_max_sharpe(historical_pricing)
        self.load_basic_results(
            portfolio, new_iteration, f"Max Sharpe_{new_iteration}", weights_max_sharpe
        )

        self.success_msg.value = f'<h4 style="color:green;">Basic optimization completed. Verify using portfolio [{portfolio}] and  iteration [{new_iteration}] and the following opt methods: <ul><li>Minimum volatility</li><li>Max Sharpe</li></ul></h4>'
        self.set_iteration(portfolio)

    def optimize_portfolio(
        self,
        opt_type,
        sector_upper={},
        sector_lower={},
        ticker_upper={},
        ticker_lower={},
    ):
        portfolio = self.portfolio_dropdown.value
        iteration = self.iteration_dropdown.value
        opt_mtd = self.opt_mtd_dropdown.value

        new_iteration = time.strftime("%Y%m%d_%X")
        new_opt_mtd = f"{opt_type}_{new_iteration}"

        historical_pricing = self.query.get_historical_pricing(
            portfolio, iteration, opt_mtd
        )

        sector_spread = self.query.get_sector_spread(
            portfolio, iteration, opt_mtd
        ).reset_index()

        sector_mapper = {}

        # ignore sector mapper if opt_type is ticker
        if (opt_type == "Sector") | (opt_type == "Portfolio"):
            # sectors
            sector_mapper = (
                sector_spread[["GICS Sector", "Tickers"]]
                .set_index("Tickers")
                .to_dict()["GICS Sector"]
            )

            # check if any sector gets excluded, i.e. upper limit is 0
            listOfKeys = [key for (key, value) in sector_upper.items() if value == 0]
            print("Sectors set to 0: ", listOfKeys)
            if len(listOfKeys) > 0:
                print("[Pre validation] Tickers upper: ", ticker_upper)
                print("[Pre validation] Tickers lower: ", ticker_lower)

                # get list of tickers under the sector
                listOfTickers = [
                    key for (key, value) in sector_mapper.items() if value in listOfKeys
                ]
                print("Tickers to be set to 0: ", listOfTickers)

                # set upper and lower limits of tickers to 0
                ticker_upper = {
                    key: 0 if key in listOfTickers else value
                    for (key, value) in ticker_upper.items()
                }
                ticker_lower = {
                    key: 0 if key in listOfTickers else value
                    for (key, value) in ticker_lower.items()
                }

                print("[Post validation] Tickers upper: ", ticker_upper)
                print("[Post validation] Tickers lower: ", ticker_lower)
            print("sector_mapper: ", sector_mapper)
        else:
            print(f"optimize {opt_type}")

        try:
            proposed_weights = self.optimizer.exec_optimization(
                historical_pricing,
                self.opt_target_radio.value,
                sector_mapper,
                sector_upper,
                sector_lower,
                ticker_upper,
                ticker_lower,
                self.target_returns.value,
            )
            print("proposed_weights", proposed_weights)

            self.load_basic_results(
                portfolio, new_iteration, new_opt_mtd, proposed_weights
            )

            print(
                f"sector_upper: {len(sector_upper)}, sector_lower: {len(sector_lower)}"
            )
            print(
                f"ticker_upper: {len(ticker_upper)}, ticker_lower: {len(ticker_lower)}"
            )

            target_returns = (
                self.target_returns.value
                if self.opt_target_radio.value == "Target returns"
                else None
            )

            if (
                (len(sector_upper) > 0)
                | (len(sector_lower) > 0)
                | (len(ticker_upper) > 0)
                | (len(ticker_lower) > 0)
            ):
                self.query.load_limits(
                    portfolio,
                    new_opt_mtd,
                    sector_spread,
                    sector_upper,
                    sector_lower,
                    ticker_upper,
                    ticker_lower,
                    target_returns,
                )

            self.set_iteration(portfolio)

        except Exception as e:
            self.success_msg.value = f'<h4 style="color:red;">[{str(e)}]</h4>'
            print("Exception in sector optimization", str(e))
        else:
            print("Optimization completed.")
            self.success_msg.value = (
                f'<h4 style="color:green;">[{opt_type}] Optimization completed.</h4>'
            )

    def get_sectors_limit(self):
        weights_lower, weights_upper = self.get_final_weights(
            self.tab_widget.children[0].children[0].children
        )
        return weights_lower, weights_upper

    def get_tickers_limit(self):
        sym_upper, sym_lower = {}, {}

        for sect in self.tab_widget.children[1].children[0].children:
            if isinstance(sect, widgets.VBox):
                weights_lower, weights_upper = self.get_final_weights(
                    sect.children[0].children
                )
                sym_lower.update(weights_lower)
                sym_upper.update(weights_upper)
        return sym_upper, sym_lower

    def submit_sector(self, b):
        sector_lower, sector_upper = self.get_sectors_limit()

        if self.warning_msg.value != "":
            self.warning_msg.value += '<h4 style="color:red;">Please check the weight spread before proceeding.</h4>'
            print("Check failed, do not proceed with optimization")
        else:
            self.warning_msg.value = ""
            self.optimize_portfolio(
                opt_type="Sector", sector_upper=sector_upper, sector_lower=sector_lower
            )

            print("Optimization submitted")

    def submit_tickers(self, b):
        sym_upper, sym_lower = self.get_tickers_limit()

        if float(self.min_sym_wid.value) > 1:
            self.warning_msg.value = '<h4 style="color:red;">Total minimum weight cannot be more than 1. Please check the weight spread before proceeding.</h4>'
            print("Check failed, do not proceed with optimization")
        else:
            self.warning_msg.value = ""
            self.optimize_portfolio(
                opt_type="Ticker", ticker_upper=sym_upper, ticker_lower=sym_lower
            )
            print("Optimization submitted")

    def submit_portfolio(self, b):
        sector_lower, sector_upper = self.get_sectors_limit()
        sym_upper, sym_lower = self.get_tickers_limit()

        self.optimize_portfolio(
            opt_type="Portfolio",
            sector_upper=sector_upper,
            sector_lower=sector_lower,
            ticker_upper=sym_upper,
            ticker_lower=sym_lower,
        )

    def set_iteration(self, portfolio):
        _iteration, _opt_mtd_opt = self.query.get_portfolio_details(portfolio)
        self.iteration_dropdown.options = _iteration
        self.iteration_dropdown.value = _iteration[0]
        self.iteration_dropdown.disabled = False

    def on_portfolio_change(self, change):
        self.set_iteration(change["new"])

        # trigger tab refresh
        self.on_opt_change(None)

    def on_iteration_change(self, change):
        _portfolio = self.portfolio_dropdown.value
        _iteration, _opt_mtd_opt = self.query.get_portfolio_details(
            _portfolio, change["new"]
        )

        self.opt_mtd_dropdown.options = _opt_mtd_opt
        self.opt_mtd_dropdown.value = _opt_mtd_opt[0]
        self.opt_mtd_dropdown.disabled = False

        self.wo_constraint_button.disabled = False
        self.sector_button.disabled = False
        self.ticker_button.disabled = False
        self.portfolio_button.disabled = False

        # trigger tab refresh
        self.on_opt_change(None)

    def on_opt_change(self, change):
        self.min_sec_wid.value = "0.0"
        self.max_sec_wid.value = "0.0"
        self.min_sym_wid.value = "0.0"
        self.max_sym_wid.value = "0.0"
        self.get_tab_content()

    def on_radio_change(self, change):
        self.target_returns.disabled = change["new"] != "Target returns"

    def get_section_total(self, section_type, content):
        if section_type == self.SECTOR_TYPE:
            self.min_sec_wid.value = str(
                float(self.min_sec_wid.value) + content.children[2].value
            )
            self.max_sec_wid.value = str(
                float(self.max_sec_wid.value) + content.children[3].value
            )
        else:
            self.min_sym_wid.value = str(
                float(self.min_sym_wid.value) + content.children[2].value
            )
            self.max_sym_wid.value = str(
                float(self.max_sym_wid.value) + content.children[3].value
            )

    def update_sector_total(self, weight_type, change):
        difference = change["new"] - change["old"]

        if weight_type == "min":
            self.min_sec_wid.value = str(
                round(float(self.min_sec_wid.value) + difference, 5)
            )
        else:
            self.max_sec_wid.value = str(
                round(float(self.max_sec_wid.value) + difference, 5)
            )

    def update_ticker_total(self, weight_type, change):

        difference = change["new"] - change["old"]

        if weight_type == "min":
            self.min_sym_wid.value = str(
                round(float(self.min_sym_wid.value) + difference, 5)
            )
        else:
            self.max_sym_wid.value = str(
                round(float(self.max_sym_wid.value) + difference, 5)
            )

    def get_header(self):
        return widgets.HBox(
            [
                widgets.Label(value="", layout=widgets.Layout(width="150px")),
                widgets.Label(
                    value="Curr. weight", layout=widgets.Layout(width="100px")
                ),
                widgets.Label(
                    value="Min. weight", layout=widgets.Layout(width="100px")
                ),
                widgets.Label(
                    value="Max. weight", layout=widgets.Layout(width="100px")
                ),
            ]
        )

    def get_content(self, section_type, float_obj):
        float_text = [
            widgets.HBox(
                [
                    widgets.Label(
                        value=key,
                        layout=widgets.Layout(
                            width="150px", display="flex", justify_content="flex-end"
                        ),
                    ),
                    widgets.BoundedFloatText(
                        value=value["current"],
                        max=1.0,
                        step=0.01,
                        disabled=True,
                        layout=widgets.Layout(width="100px"),
                    ),
                    widgets.BoundedFloatText(
                        value=value["min"],
                        max=1.0,
                        step=0.01,
                        disabled=False,
                        layout=widgets.Layout(width="100px"),
                    ),
                    widgets.BoundedFloatText(
                        value=value["max"],
                        max=1.0,
                        step=0.01,
                        disabled=False,
                        layout=widgets.Layout(width="100px"),
                    ),
                ]
            )
            for key, value in float_obj.items()
        ]

        for box in float_text:
            self.get_section_total(section_type, box)
            if section_type == self.SECTOR_TYPE:
                box.children[2].observe(
                    functools.partial(self.update_sector_total, "min"),
                    names=["value"],
                )
                box.children[3].observe(
                    functools.partial(self.update_sector_total, "max"),
                    names=["value"],
                )
            else:
                box.children[2].observe(
                    functools.partial(self.update_ticker_total, "min"),
                    names=["value"],
                )
                box.children[3].observe(
                    functools.partial(self.update_ticker_total, "max"),
                    names=["value"],
                )

        obj_len = len(float_obj)
        num_header = 3 if obj_len > 3 else obj_len
        display_width = 1500 if num_header == 3 else ((1500 / 3) * num_header)

        headers = [self.get_header() for i in range(0, num_header)]

        ft_cont = widgets.HBox(
            layout=widgets.Layout(
                width=f"{str(display_width)}px",
                display="inline-flex",
                flex_flow="row wrap",
            )
        )

        ft_cont.children = headers + [i for i in float_text]
        return ft_cont

    def get_float_text(self, float_obj):
        ft_cont = self.get_content(self.SECTOR_TYPE, float_obj)
        return [ft_cont, self.hr]

    def get_ticker_section(self, float_obj, sector_spread):
        title = []
        sector_acc_child = []
        for sec_label, sym_df in sector_spread.groupby(level=0):
            title.append(sec_label)

            sector_tickers = dict(
                (k, float_obj[k])
                for k in sym_df.index.get_level_values(1).to_list()
                if k in float_obj
            )

            sector_acc_child.append(
                widgets.VBox([self.get_content(self.TICK_TYPE, sector_tickers)])
            )

        return [widgets.Accordion(children=sector_acc_child, titles=tuple(title))]

    def get_tab_content(self):
        _portfolio = self.portfolio_dropdown.value
        _iteration = self.iteration_dropdown.value
        _opt_mtd = self.opt_mtd_dropdown.value

        ticker = self.query.get_weights(_portfolio, _iteration, _opt_mtd, "Tickers")
        sector = self.query.get_weights(_portfolio, _iteration, _opt_mtd, "GICS Sector")
        sector_spread = self.query.get_sector_spread(_portfolio, _iteration, _opt_mtd)

        sector_float_text = self.get_float_text(sector)
        ticker_float_text = self.get_ticker_section(ticker, sector_spread)

        sector_summary = widgets.HBox([self.min_sec_wid, self.max_sec_wid])
        sector_float_text.append(sector_summary)

        tickers_summary = widgets.HBox([self.min_sym_wid, self.max_sym_wid])
        ticker_float_text.append(tickers_summary)

        tab_children = [
            widgets.VBox(sector_float_text),
            widgets.VBox(ticker_float_text),
        ]

        self.tab_widget.children = tab_children
        self.tab_widget.titles = ["Sectors", "Tickers"]
        self.tab_widget.disabled = False

    def display(self):
        display(
            widgets.VBox(
                [
                    widgets.HBox(
                        [
                            self.portfolio_dropdown,
                            self.iteration_dropdown,
                            self.opt_mtd_dropdown,
                        ]
                    ),
                    widgets.HBox([self.opt_target_radio, self.target_returns]),
                    self.hr,
                    widgets.HBox(
                        [
                            self.wo_constraint_button,
                            self.sector_button,
                            self.ticker_button,
                            self.portfolio_button,
                        ]
                    ),
                    self.success_msg,
                    self.hr,
                    self.tab_widget,
                    self.warning_msg,
                    self.styling,
                ]
            )
        )
