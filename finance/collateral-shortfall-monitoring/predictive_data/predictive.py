import pandas as pd
import numpy as np
from datetime import date, timedelta

def generate_assets()-> pd.DataFrame:
    assets = []
    assets.append({'Asset_Code':'BNP.PA','Sector':'Financial Services','Country':'France','Haircut':0.10})
    assets.append({'Asset_Code':'CA.PA','Sector':'Consumer Defensive','Country':'France','Haircut':0.10})

    assets.append({'Asset_Code':'AC.PA','Sector':'Consumer Cyclical','Country':'France','Haircut':0.10})
    assets.append({'Asset_Code':'ENGI.PA','Sector':'Utilities','Country':'France','Haircut':0.10})

    assets.append({'Asset_Code':'CAP.PA','Sector':'Technology','Country':'France','Haircut':0.10})
    assets.append({'Asset_Code':'SAN.PA','Sector':'Healthcare','Country':'France','Haircut':0.10})

    assets.append({'Asset_Code':'G.MI','Sector':'Financial Services','Country':'Italy','Haircut':0.10})
    assets.append({'Asset_Code':'RACE.MI','Sector':'Consumer Cyclical','Country':'Italy','Haircut':0.10})

    assets.append({'Asset_Code':'TIT.MI','Sector':'Communication Services','Country':'Italy','Haircut':0.10})
    assets.append({'Asset_Code':'JUVE.MI','Sector':'Consumer Cyclical','Country':'Italy','Haircut':0.10})

    assets.append({'Asset_Code':'FCA.MI','Sector':'Consumer Cyclical','Country':'Italy','Haircut':0.10})
    assets.append({'Asset_Code':'ENI.MI','Sector':'Energy','Country':'Italy','Haircut':0.10})
    
    assets_df = pd.DataFrame(assets)
    return assets_df

def generate_prices(asset_last_day_df, from_date, horizon, forward, mean):
    assets_df = generate_assets()
    number_of_dates = horizon
    dates = [from_date + forward*timedelta(days=x) for x in range(1, number_of_dates)]
    assets_value = []
    for index, row in assets_df.iterrows():
        asset_code = row["Asset_Code"]
        for d in dates:
            year_month = d.strftime('%Y-%m')
            noise = np.random.normal(mean, 0.02)
            asset_value = (1 + noise) * 100;
            new_row = [asset_code, d, asset_value, year_month]
            assets_value.append(new_row)
        
    assets_value_df = pd.DataFrame(data=assets_value, columns=['Asset_Code','Date','Price', 'Year_Month'])
    return pd.concat([asset_last_day_df, assets_value_df]);