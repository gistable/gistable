import pandas as pd
import numpy as np
import instrumentdb as idb
import math
import pickle

def good_entries(ohlcv, min_days = 3, days_out = 15, vola_len = 35, days_pos = 0.6, stop_loss = 1.5):
    if days_out <= min_days:
        raise RuntimeError('days_out must be greater than min_days.')

    hi = ohlcv['high']
    lo = ohlcv['low']
    cl = ohlcv['close']

    # Compute returns
    rets = cl.pct_change()
    erets = rets.pow(2).ewm(span=vola_len).mean().pow(1/2)
    # erets = rets.ewm(span=vola_len).mean()

    res = np.zeros(len(erets))
    days = np.zeros(len(erets))

    for ii in range(min_days, days_out):
        hh = hi.rolling(window = ii).max().shift(-ii)
        ll = lo.rolling(window = ii).min().shift(-ii)
        hi_ratio = (hh/cl - 1)/erets
        lo_ratio = (ll/cl - 1)/erets

        dd = math.ceil(days_pos * ii)

        longs = (hi_ratio > dd) & (-lo_ratio < stop_loss)
        longs = np.where(longs.notnull() & (longs != 0), 1, 0)

        shorts = (-lo_ratio > dd) & (hi_ratio < stop_loss)
        shorts = np.where(shorts.notnull() & (shorts != 0), -1, 0)

        both = np.where(longs == 1, 1, shorts)
        new_days = ii*((res == 0) & (both != 0)).astype(int)
        res = np.where(res != 0, res, both)
        days = np.where(days != 0, days, new_days)

    full_df = pd.DataFrame({'entry' : res, 'days' : days, 'erets' : erets}, index = ohlcv.index)
    oppo_df = full_df[full_df['entry'] != 0]

    return {'full' : full_df, 'oppo' : oppo_df}

def build_features(ohlcv, days=[1,2,3,4,5], vola_len=35):
    cl = ohlcv['close']
    rets = cl.pct_change()
    erets = rets.pow(2).ewm(span=vola_len).mean().pow(1/2)
    ares = rets / erets
    res = ares.shift(days[0] - 1)
    col_names = [str(days[0]) + "D_LAG"]
    for dd in days[1:]:
        res = pd.concat([res, ares.shift(dd - 1)], axis=1)
        col_names.append(str(dd) + "D_LAG")

    # Annual, quarterly, monthly and weekly:
    #   1. returns (normalized to daily)
    #   2. min/max channel position
    for nn in [252, 63, 21, 5]:
        # Compute the return
        rr = cl.pct_change(nn)
        # Normalize to daily return
        rr = ((rr/100 + 1).pow(1/nn) - 1)*100
        # Normalize by volatility
        rr = rr / erets
        res = pd.concat([res, rr], axis=1)
        col_names.append(str(nn) + "D_RET")
        rr = (cl - cl.rolling(window=nn).min())/(cl.rolling(window=nn).max() - cl.rolling(window=nn).min())
        res = pd.concat([res, rr], axis=1)
        col_names.append(str(nn) + "D_CHANNEL")

    res.columns = col_names
    res = res.dropna(axis=0)

    return res