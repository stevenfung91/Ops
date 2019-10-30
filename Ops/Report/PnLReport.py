'''
Run PnL Report from all-exchange report and borrow report
'''

import os, datetime
from Data.LoadBalance import BalanceReport
from Utils.CONFIG import *
import pandas as pd

GRIDMM_STRATS = ['gridmmIco1', 'gridmmIco2', 'gridmmIco3', 'gridmmIco4', 'gridmmIco5', 'gridmmIco6',
                 'gridmmIco7', 'gridmmIco8', 'gridmmIco9', 'gridmmIco10', 'gridmmIco11', 'gridmmIco12',
                 'gridmmIco13', 'gridmmIco14', 'gridmmIco15', 'gridmmIco16', 'gridmmIco17', 'gridmmIco18',
                 'gridmmIco19', 'gridmmIco20', 'gridmmIco21', 'gridmmIco22', 'gridmmIco23', 'gridmmIco24',
                 'gridmmIco25', 'gridmmIco26', 'gridmmHt', 'gridmmIcoht1', 'gridmmIcoht2']

DEPTHCOPY_STRATS = ['binanceDc', 'binanceDc1', 'binancedceth', 'binancedchusd', 'binancedcusdt', 'binancedcusdt1',
                    'okexdcusdt', 'triarbmmprobtc', 'triarbmmprohpt', 'triarbmmprohusd', 'triarbmmprousdt', 'prohusddc',
                    'triarbmmstable']

SELFTRADING_STRATS = ['selfTradingBigCoin', 'selfTradingHPT', 'gridmmEOS', 'selfTradingEOS', 'mmStd', 'mmStdHusd',
                      'gridmmbigcoin']

PRO_STRATS = GRIDMM_STRATS + DEPTHCOPY_STRATS + SELFTRADING_STRATS
HBKR_STRATS = ['gridmmkorea']
HBJP_STRATS = ['gridmmJapan1', 'gridmmJapan2']


class PnLReport:
    """
    Date: YYYY-MM-DD
    """
    def __init__(self, inputfile, date):
        self.date = str(date)
        self.inputfile = inputfile
        self._load_all()

    def _load_all(self):
        self._load_path()
        self._load_balance()
        self._load_price()
        self._load_borrow()

    def _load_balance(self, criteria=None, accounts=None, exchanges=None, strategies=None):
        # Load Balance
        bal = BalanceReport(self.inputfile, self.date)
        if criteria is None:
            self.balance = bal.df
        if criteria == 'account' and isinstance(accounts, list) and len(accounts) > 0:
            self.balance = bal.sort_by_accounts(accounts)
        if criteria == 'exchange' and isinstance(exchanges, list) and len(exchanges) > 0:
            self.balance = bal.sort_by_exchanges(exchanges)
        if criteria == 'strategy' and isinstance(strategies, list) and len(strategies) > 0:
            self.balance = bal.sort_by_strategies(strategies)

    def _load_path(self):
        self.price_path = REPORT_PATH + 'price/price_%s-00-00.csv' % self.date
        self.borrow_path = REPORT_PATH + 'borrow_new/borrow_%s-00-00.xlsx' % self.date
        #print(self.price_path)
        #print(self.borrow_path)

    def _load_borrow(self):
        if not os.path.exists(self.borrow_path):
            from Data.LoadBorrow import run
            run()
        self.borrows = pd.read_excel(self.borrow_path, index_col='Unnamed: 0')

    def _load_price(self):
        df = pd.read_csv(self.price_path)
        df = df[['coin', 'price']]
        df.set_index('coin', inplace=True)
        sr = pd.Series(df['price'], index=df.index)
        self._adjusted_price(sr)
        self.price = sr

    def _adjust_balance_account(self, balance):
        OBSOLETE_ACC_IDS = ['gridmmIco1']
        OBSOLETE_ACC_IDS = [x.lower() for x in OBSOLETE_ACC_IDS]
        balance.drop(columns=['bch'], inplace=True)
        for acc_id in OBSOLETE_ACC_IDS:
            if acc_id in balance.index:
                balance = balance.drop(acc_id)
        return balance

    def _adjusted_price(self, sr):
        sr['husd'] = sr['usdt']
        sr['usdt'] = 1.00

    def cal_pnl(self, stratList):
        # Balance
        self._load_balance(criteria='strategy', strategies=stratList)
        balance = self._adjust_balance_account(self.balance)
        balance['acc_id'] = balance.index
        balance.index = balance['strategy']
        balance.drop(columns=['strategy'], inplace=True)
        # balance.set_index(['exchange', 'strategy', 'uid'], inplace=True)
        index_col = ['exchange', 'acc_id', 'uid']
        coin_col = [x for x in list(balance.columns) if x not in index_col]
        frame_index = balance[index_col]
        main_bal = balance[coin_col]
        main_bal = main_bal.groupby(level=0).sum()
        # Borrow
        borrows = self.borrows.reindex(stratList)
        # PnL
        pnl = main_bal.subtract(borrows, fill_value=0)
        '''
        print('info')
        frame_index = frame_index.sort_index()
        print(frame_index)

        print('balance')
        main_bal = main_bal.fillna(0)
        main_bal = main_bal.loc[:, (main_bal != 0).any(axis=0)]
        main_bal.sort_index(inplace=True)
        print(main_bal)

        print('borrow')
        borrows = borrows.fillna(0)
        borrows = borrows.loc[:, (borrows != 0).any(axis=0)]
        borrows.sort_index(inplace=True)
        print(borrows)
         '''

        print("pnl")
        pnl = pnl.fillna(0)
        pnl = pnl.loc[:, (pnl != 0).any(axis=0)]
        pnl.sort_index(inplace=True)
        print(pnl)

        print("pnl_usdt")
        pnl_usdt = pnl * self.price
        pnl_usdt = pnl_usdt.fillna(0)
        pnl_usdt.loc[:, 'sum'] = pnl_usdt.sum(axis=1)
        pnl_usdt.sort_index(inplace=True)
        print(pnl_usdt.to_string())

        # Format DataFrame
        return {'pnl': pnl, 'pnl_usdt': pnl_usdt, 'borrow': borrows, 'info': frame_index, 'price': self.price}

    def cal_delta(self, stratList, currency, threshold):
        res = self.cal_pnl(stratList)
        pnl_usdt_frame = res['pnl_usdt']
        pnl_usdt_frame.drop(columns=['sum'], inplace=True)

        # Greater Than 10k USDT
        currencyDict = {'usdt': 1, 'jpy': 100, 'krw': 1000}
        threshold *= currencyDict.get(currency, 1)
        print('Greater Than %d' % threshold)
        res = pnl_usdt_frame[(pnl_usdt_frame.iloc[:] > threshold) | (pnl_usdt_frame.iloc[:] < -threshold)]
        res.dropna(how='all', axis=0, inplace=True)
        res.dropna(how='all', axis=1, inplace=True)
        return res

    def cal_pro_pnl(self):
        return self.cal_pnl(PRO_STRATS)

    def cal_hbkr_pnl(self):
        HBKR_STRATS = ['gridmmkorea', 'koreadc', 'triarbmmkoreaw']
        return self.cal_pnl(HBKR_STRATS)

    def cal_hbgeos_pnl(self):
        HBGEOS_STRATS = ['gridmmEOS', 'selfTradingHPT']
        return self.cal_pnl(HBGEOS_STRATS)

    def run_pnl_report(self):
        pass

    def run_delta_report(self, currency, threshold, outfile=False):
        report_path = REPORT_PATH + "/delta/" + "delta_%s_thrs_%d.xlsx" % (self.date, threshold)
        if currency == 'usdt':
            res = self.cal_delta(PRO_STRATS, currency, threshold)
            if len(res) > 0 and outfile:
                res.index.name = 'strategy'
                res.fillna(0, inplace=True)
                res.to_excel(report_path)


if __name__ == "__main__":
    date = '2019-10-30'
    pnl = PnLReport('all_exchange', date)
    # hbkr = pnl.cal_hbkr_pnl()
    # hbgoes = pnl.cal_hbgeos_pnl()
    # print(pnl.balance)
    pro = pnl.cal_pro_pnl()
    #for curr in [1000, 5000, 10000]:
    #    delta = pnl.run_delta_report('usdt', curr, outfile=True)

    # pro['pnl'].to_excel("D:/Docs/test_gridMM1026.xlsx")
    #print(hbgoes)
