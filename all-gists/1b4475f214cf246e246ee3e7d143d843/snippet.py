'''
A module to load instruments and bars from a SQLite database.
'''

import pandas as pd
import toml

from sqlalchemy import create_engine

class CsiDb:
    def __init__(self, config_path = "csidb.toml"):
        self.configs = {'provider' : 'csi', 'flavor' : 'SQLite', 'bars_table' : 'csi_bars'}
        with open(config_path) as config_file:
            self.configs.update(toml.loads(config_file.read()))
        return
    
    def mload_bars(self, symbols = None):
        engine = create_engine(self.configs["db"])
        conn = engine.connect()
        
        if not symbols:
            symbols = self.future_list()

        conn.close()

        res = {}
        for symbol in symbols:
            res[symbol] = self.load_bars(symbol)

        return res
    
    def load_bars(self, symbol, ohlc=True, index_column='ts'):
        engine = create_engine(self.configs["db"])
        conn = engine.connect()

        columns = None
        if ohlc:
            columns = 'open,high,low,close'
        else:
            columns = 'open,high,low,close,volume,interest,closing_bid,closing_ask'
        
        query = (" SELECT date(ts/1000,'unixepoch') as ts," + columns + " "
                 " FROM " + self.configs['bars_table'] + " "
                 " WHERE symbol = '" + symbol + "' "
                 " ORDER BY ts ASC")
               
        res = pd.read_sql_query(sql = query, con = conn)
        conn.close()

        # Set the index to the timestamp column
        aa = res.ix[:, res.columns != index_column]
        colnames = aa.columns

        res = pd.DataFrame(aa.as_matrix(), index=res[index_column], columns=colnames)

        return res
    
    def future_list(self):
        engine = create_engine(self.configs["db"])
        conn = engine.connect()
        # where_clause = "provider = '" + self.configs["provider"] + "' and type = 'FUT'"
        # query = select(columns=[column('symbol'),column('bpv'),column('tick'),column('comment'),column('min_move')], whereclause=where_clause, from_obj=text("instrument"))
        query = "select symbol, bpv, tick, comment, min_move from instrument where provider = '" + self.configs['provider'] + "' and type = 'FUT'"
        res = pd.read_sql_query(sql = query, con = conn)
        conn.close()
        return res