import os
import sys
import importlib
import pandas as pd
import datetime
import git
from Utils.CONFIG import *


def _borrow_config(strategy_name):
    sys.path.append(BORROW_CONFIG_PATH)
    strategy_file_name = strategy_name + '_cfg'
    path = BORROW_CONFIG_PATH + strategy_file_name + '.py'
    if not os.path.exists(path):
        return None
    # print(path)
    m1 = importlib.import_module(strategy_file_name)
    # print(m1)

    variables = dir(m1)
    strat_dict = {}

    if 'init_borrow' in variables:
        strat_dict = m1.init_borrow
    elif 'borrow' in variables:
        strat_dict = m1.borrow

    if len(strat_dict) == 0:
        sorted_variables = [x for x in variables if x.endswith('borrow')]

        for mod in sorted_variables:
            borrow_amount = getattr(m1, mod)
            coin = mod.split('_')[0]
            if coin not in strat_dict:
                strat_dict[coin] = borrow_amount
            else:
                strat_dict[coin] += borrow_amount

    strat_dict['name'] = strategy_name
    return strat_dict


def _load_all_strategies(path=ACC_ID_PATH, reportline=['PRO']):
    df = pd.read_csv(path)
    df = df[df['report'].isin(reportline)]
    strategies = df['strategy'].values.tolist()
    strategies = list(set(strategies))
    return strategies


def update_from_git():
    g = git.cmd.Git(GIT_PATH)
    g.pull()


if __name__ == "__main__":
    name =_load_all_strategies(reportline=['HBGEOS'])
    config = _borrow_config('selfTradingEOS')
    print(name)
    print(config)