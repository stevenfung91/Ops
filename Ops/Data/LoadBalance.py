"""
GET EXCHANGE(S) BALANCE
"""
import pandas as pd
import datetime
from Utils.CONFIG import *


class BalanceReport:
    def __init__(self, inputfile, datestr=None):
        self.inputfile = inputfile
        self.datestr = datetime.datetime.now().strftime('%Y-%m-%d') if datestr is None else datestr
        assert self.inputfile in ['operation', 'all_exchange'], "wrong inputfile param"

        filename = self.inputfile + "_" + datestr + '-00-00.csv'
        self.inpath = REPORT_PATH + "%s/%s" % (self.inputfile, filename)
        self._load_accID()
        self._load_balance(inputfile)

    def _load_accID(self):
        acct_frame = pd.read_csv(ACC_ID_PATH)
        self.acc_id_df = acct_frame.apply(lambda x: x.str.strip(), axis=1)

    def _load_balance(self, inputfile):
        if inputfile == 'all_exchange':
            self.df = self.get_all_exchange_balance()
        if inputfile == 'operation':
            self.df = self.get_operation_balance()
        if self.df.empty:
            raise ValueError("cannot retrieve %s dataset" % self.inputfile)
        else:
            self.df = self._map_strategy()

    def get_all_exchange_balance(self):
        df = pd.read_csv(self.inpath)
        df = df.fillna(0)
        return df

    def get_operation_balance(self):
        df = pd.read_csv(self.inpath)
        df = df.fillna(0)
        df.set_index('name', inplace=True)
        return df

    def get_uid_list(self):
        uid_list = list(self.acc_id_df['uid'])
        return uid_list

    def filter_dataframe(self, df, removezero):
        if self.inputfile == 'all_exchange':
            # df.drop(['Unnamed: 0'], axis=1, inplace=True)
            df.set_index(['acc_id'], inplace=True)

        if self.inputfile == 'operation':
            df.set_index(['acc_id'], inplace=True)

        if removezero:
            df = df.loc[:, (df != 0).any(axis=0)]

        return df

    def _map_strategy(self):
        acc_frame = self.acc_id_df[['acc_id', 'exchange', 'strategy', 'uid']]
        bal_frame = self.df
        bal_frame.rename({'name': 'acc_id'}, axis='columns', inplace=True)
        bal_frame.drop(columns=['Unnamed: 0'], inplace=True)

        res = bal_frame.merge(acc_frame, on=['acc_id', 'exchange'], how='left', suffixes=('', '_new'))  # 這兩行程式是全等的
        for col in ['uid', 'strategy']:
            res[col] = res[col+"_new"]
            res.drop(columns=[col+"_new"], inplace=True)
        res = res[res['strategy'].notnull()]
        return res

    def sort_by_exchanges(self, exchs, removezero=False):
        if exchs is not None:
            if isinstance(exchs, list):
                df = self.df[(self.df['exchange'].isin(exchs))]
            elif isinstance(exchs, str):
                df = self.df[(self.df['exchange'] == exchs)]
            else:
                raise TypeError('wrong exchange input format')
            return self.filter_dataframe(df, removezero)

    # GET ACCOUNT(S) BALANCE
    def sort_by_accounts(self, accounts, removezero=False):
        if accounts is not None:
            if isinstance(accounts, list):
                df = self.df[(self.df['acc_id'].isin(accounts))]
            elif isinstance(accounts, str):
                df = self.df[(self.df['acc_id'] == accounts)]
            else:
                raise TypeError('wrong exchange input format')
            return self.filter_dataframe(df, removezero)

    def sort_by_strategies(self, strategies, removezero=False):
        if strategies is not None:
            if isinstance(strategies, list):
                df = self.df[(self.df['strategy'].isin(strategies))]
            elif isinstance(strategies, str):
                df = self.df[(self.df['strategy'] == strategies)]
            else:
                raise TypeError('wrong exchange input format')
            return self.filter_dataframe(df, removezero)

    def sort_by_uids(self, getuid=False, uids=None):
        if getuid:
            uids = self.get_uid_list()

        if self.inputfile == 'operation':
            raise TypeError("cannot sort uid from operation file")
        if self.inputfile == 'all_exchange':
            if uids is not None:
                if isinstance(uids, list):
                    df = self.df[(self.df['uid'].isin(uids))]
                elif isinstance(uids, str) or isinstance(uids, int):
                    df = self.df[(self.df['uid'] == uids)]
                else:
                    raise TypeError('wrong dataframe format')
                return self.filter_dataframe(df)


if __name__ == "__main__":
    balance = BalanceReport('all_exchange', '2019-10-30')
    acc = balance.sort_by_accounts(['gridmmkorea','koreandc', 'triarbmmkorea'], removezero=True)
    exch = balance.sort_by_exchanges(['hbkr','hbjp'])
    stra = balance.sort_by_strategies(['binanceDc', 'selfTradingBigCoin', 'SCSR'], removezero=True)

    '''
    #print(exch)
    # print(ACC_ID_PATH)
    print(balance.df[balance.df['acc_id'].isin(['binancedcnew', 'binancedc', 'SCSR', 'selfTradingMain'])].to_string())
    print(balance.df[balance.df['strategy'].isin(['binanceDc','selfTradingBigCoin', 'SCSR'])].to_string())
    '''

    print(acc.to_string())
    print('-'*100)
    print(stra.to_string())
    #print(balance.df[balance.df['strategy'].isnull()])

