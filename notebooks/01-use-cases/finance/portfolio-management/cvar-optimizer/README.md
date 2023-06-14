# Running portfolio optimization in Atoti

In this use case, we look at how we could integrate the Python library, [PyPortfolioOpt](https://pyportfolioopt.readthedocs.io/en/latest/index.html) into [Atoti](https://www.atoti.io/) to perform portfolio optimization analysis within one single platform.

<img src="https://data.atoti.io/notebooks/cvar-optimisation/img/python_libraries.png" />

<br/>

## Running Atoti BI analytics platform 

Run [main.ipynb](./main.ipynb) before accessing the web application using http://localhost:10010/#/dashboard/0c7.

Using Atoti, we can evaluate the performance of the portfolio and compare the optimized portfolio against the initial.  

<img src="https://data.atoti.io/notebooks/cvar-optimisation/img/benchmarking.gif" />

<br/> 

## Data preparation - Historical stock pricing 

In the python script [tickers.py](./utils/tickers.py), we created functions to download 3 years of historical data from yahoo Finance using the Python library [yfinance](https://pypi.org/project/yfinance/).

Refer to the notebook [01_data_generation.ipynb](./01_data_generation.ipynb) to see how we could invoke the script.

We could upload the historical pricing into Atoti and make use of Atoti to compute the rate of returns. However, in this case, we perform the fact-level preprocessing and convert the data for each stock into an array list before loading into Atoti. 

<img src="https://data.atoti.io/notebooks/cvar-optimisation/img/data_format.png" />

Atoti comes with a set of [array functions](https://docs.atoti.io/latest/lib/atoti/atoti.array.html) that allow us to manipulate large data volume as an array, and henceforth reduce the memory footprint.

## Portfolio optimization

In the Python script [pyPortfolioOpt.py](./utils/pyPortfoliOpt.py), we consolidate a few optimization algorithms from PyPortfolioOpt that will return us the optimal weights for the portfolio:
    - minimum CVaR
    - max sharpe
    - minimum volatility
    - hierarchical risk parity portfolio optimization

The function expects the historical pricing of the stocks in the portfolio, along with the initial weights. The initial weights of the stocks are used by the minimum volatility algorithm to improve the returns.

## Integration

We could integrate the downloading of historical pricing from yfinance and the optimization of portfolios either by 
1. using [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) in Jupyter Lab.
2. customizing Atoti UI using <img src="https://img.shields.io/badge/🔒-Atoti-291A40" />.  

<img src="https://data.atoti.io/notebooks/cvar-optimisation/img/system_design3.png" />  

<br />

### yfinance

Each time user uploads a new portfolio with an initial set of weights, we trigger the download of portfolios from yfinance. This will refresh the historical pricing for all the stocks in the cube to 3 years from the upload date.

<br />

### Portfolio Optimizer

Users will be able to choose the portfolio they want to optimize from either the ipywidgets component or Atoti custom UI.  

Triggering the optimization will trigger the download of the following data to the optimizer:
1. historical pricing
2. initial weights

The proposed weights will be inserted into the cube as a new iteration for the portfolio, under the corresponding optimization method.