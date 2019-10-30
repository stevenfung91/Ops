import os
import pandas as pd
from Utils import util as ul

df = pd.read_excel('D:/Docs/Borrows/2019.10.15.xlsx')
df.index = df['name']
xf = df.loc['triarbmmpro1']
xf = xf.fillna(0)
xf.drop(['uids','name'], inplace=True)
xf = pd.to_numeric(xf)
xf = (xf[xf > 0])

CSV_PATH = "D:/OneDrive - Huobi Global Limited/config/borrow/"
strategy_name = 'triarbmmpro1'
file_path = CSV_PATH + strategy_name + '_cfg.csv'
xf.to_csv(file_path, header=False)
