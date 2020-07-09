import numpy as np
import QuantLib as ql
import pandas as pd

def reprice_trade(spot_price, trade, calc_date):
    # This function takes option trade object and spot prices and computes valuation and risk metrics.
    # Volatility and interest rates are set to some constants for simplicity.
    
    calculation_date = ql.Date(calc_date.day, calc_date.month, calc_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
        
    # conventions
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates()
    volatility = 0.3
    dividend_rate = 0.0163
    risk_free_rate = 0.001

    maturity = trade["Maturity"]
    
    maturity_date = ql.Date(
        maturity.day, maturity.month, maturity.year
    )
    option_type = ql.Option.Call if trade.OptionType == "Call" else ql.Option.Put
    strike_price = trade.Strike

    # construct the European Option
    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity_date)
    european_option = ql.VanillaOption(payoff, exercise)

    # The Black-Scholes-Merto process is constructed here.
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, risk_free_rate, day_count)
    )
    dividend_yield = ql.YieldTermStructureHandle(
        ql.FlatForward(calculation_date, dividend_rate, day_count)
    )
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
    )
    bsm_process = ql.BlackScholesMertonProcess(
        spot_handle, dividend_yield, flat_ts, flat_vol_ts
    )

    european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

    return {
        "AsOfDate": calc_date.strftime("%Y-%m-%d"),
        "TradeId": trade["TradeId"],
        "RiskFactor": trade["Ticker"],
        "MarketValue": european_option.NPV(),
        "Delta": european_option.delta() * spot_price * trade["Quantity"],
    }

def reprice_portfolio(market_data, positions, calc_date):
    # This function reprices trades and greeks if market data is available,
    # and returns new risk numbers as a dataframe
    risk = []
    for i, trade in positions.iterrows():
        spot_price_update = market_data[trade["Ticker"]]
        if not np.isnan(spot_price_update):
            risk = risk + [reprice_trade(spot_price_update, trade, calc_date)]
    return pd.DataFrame(data = risk)