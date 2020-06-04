import pandas as pd
import yfinance as yf

from datetime import date

def var_simulation(period)-> pd.DataFrame:
    # Downloading historical stock prices based on the period stated
    prices = yf.download("^GSPC ^DJI GOOG AAPL MSFT OGZPY LUKOY ROSYY", period = period)
    
    # To keep it simple, we'll mock up VaR simulations using historical stock price data returns. 
    # In this notebook we want to focus on in-memory aggregation & analytics.
    # Please refer to our other notebooks for sophisticated VaR calculation methods.
    returns = prices[['Adj Close']].pct_change()
    returns.columns = returns.columns.droplevel()
    returns = returns.dropna()

    return returns

def get_positions():
    positions = pd.DataFrame(data = [('US Indices', '^DJI', 1000),
             ('US Indices', '^GSPC', 1000),
             ('US Technology CFD', 'AAPL', -500),
             ('US Technology CFD', 'GOOG', 600),
             ('MSCI stocks', 'LUKOY', -100),
             ('MSCI stocks', 'OGZPY', -200),
             ('MSCI stocks', 'ROSYY', 200),
             ('MSCI stocks', 'SBRCY', 200)], columns = ['Book', 'Stock', 'AmountUSD'])
    return positions

def scenarios(year):
    positions = get_positions()
    
    current_year = date.today().year
    num_years = current_year - year
    period = str(num_years) + "y"
    
    returns = var_simulation(period)
    returns_series = returns.T.astype(str).apply(';'.join, axis=1)
    returns_df = pd.DataFrame({'Stock':returns_series.index, 'Values':returns_series.values})
    
    return pd.merge(positions, returns_df, on=["Stock"]), returns.index.to_pydatetime()
