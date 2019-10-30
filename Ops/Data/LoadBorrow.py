import os, csv, datetime
import pandas as pd
from Utils import util as ul
from Utils.CONFIG import *



def _all_strat_config():
    strats = ul._load_all_strategies()
    for strategy in strats:
        path = BORROW_CONFIG_PATH + strategy + "_cfg.py"
        if not os.path.exists(path):
            print(strategy)


def manual_update_config(strategy_name, params):
    # Generate Borrow Config File
    '''
    params = {
        'btc': 490,
        'eth': 9962,
        'usdt': 0,
        'ltc': 0,
        'ht': 478000,
    }
    '''

    for coin in list(params.keys()):
        if params[coin] == 0:
            params.pop(coin)

    file_path = CONFIG_PATH + "borrow/" + strategy_name + '_cfg.csv'
    df = pd.Series(params)
    df.to_csv(file_path, header=False)


def load_borrow_config_from_git(CATEGORIES):
    ROOT_PATH = 'D:/OneDrive - Huobi Global Limited/LiquidityTeam/Finance/config/borrow/'
    ul.update_from_git()
    strats = ul._load_all_strategies(reportline=CATEGORIES)

    for strat in strats:
        #print(strat)
        strat_config = ul._borrow_config(strat)
        if strat_config:
            #print(strat_config)
            name = strat_config['name']
            f = open(ROOT_PATH + name + '_cfg.csv', 'w+', newline='')
            csvwriter = csv.writer(f, delimiter=',')
            ls = list()
            for coin in sorted(strat_config.keys()):
                if coin != 'name':
                    row = [coin, strat_config[coin]]
                    ls.append(row)

            csvwriter.writerows(ls)
            f.close()


def run_borrow_report(CATEGORIES, OUTPUT=False):
    gf = pd.DataFrame()
    REPORT_PATH = 'D:/OneDrive - Huobi Global Limited/LiquidityTeam/Finance/Reports/borrow_new/'
    datestr = datetime.datetime.now().strftime('%Y-%m-%d-00-00')
    strats = ul._load_all_strategies(reportline=CATEGORIES)
    for strat in strats:
        FILENAME = '%s_cfg.csv' % strat
        # print(FILENAME)
        path = LOCAL_BORROW_CONFIG_PATH + FILENAME
        if os.path.exists(path):
            df = pd.read_csv(LOCAL_BORROW_CONFIG_PATH + FILENAME, names=['coin', strat])
            xf = df.transpose()
            xf.columns = df['coin']
            xf.drop(['coin'], inplace=True)
            # int(xf)
            gf = gf.add(xf, fill_value=0)
            # print(xf)
    gf = gf.fillna(0)
    # gf.index = df['']
    print(gf.to_string())
    print("-"*50)
    if OUTPUT:
        OUTPUTFILE = 'borrow_%s.xlsx' % datestr
        gf.to_excel(REPORT_PATH + OUTPUTFILE)

    # df.to_csv(REPORT_PATH + FILENAME)


def run():
    CATEGORIES = ['PRO', 'BUYSIDE', 'HBGEOS', 'HBKR', 'HBJP']

    load_borrow_config_from_git(CATEGORIES)
    run_borrow_report(CATEGORIES, OUTPUT=True)


if __name__ == "__main__":
    # run()
    manual_update_config(strategy_name='otcglobal', params={'usdt': 10000})