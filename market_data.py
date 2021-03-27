import etherscan as es
from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import datetime as dt
import time
from functools import reduce
import matplotlib.pyplot as plt

# Global variables
cg_api    = CoinGeckoAPI()
coin_dict = pd.DataFrame(cg_api.get_coins_list())

class MarketData:

    def __init__( self, token, currency ):
        self.token_list = token
        self.currency   = currency

    def last_price( self ):
        if type(self.token_list) == list:
            px = {}
            for tkn in self.token_list:
                px[tkn] = cg_api.get_coin_by_id(tkn)['market_data']['current_price'][self.currency]
            return px
        elif type(self.token_list) == str:
            px = cg_api.get_coin_by_id(self.token_list)['market_data']['current_price'][self.currency]
            return px

    def px_last( self ):
        return self.last_price()

    def high_24h( self ):
        if type(self.token_list) == list:
            px = {}
            for tkn in self.token_list:
                px[tkn] = cg_api.get_coin_by_id(tkn)['market_data']['high_24h'][self.currency]
            return px
        elif type(self.token_list) == str:
            px = cg_api.get_coin_by_id(self.token_list)['market_data']['high_24h'][self.currency]
            return px

    def px_high( self ):
        return self.high_24h()

    def low_24h( self ):
        if type(self.token_list) == list:
            px = {}
            for tkn in self.token_list:
                px[tkn] = cg_api.get_coin_by_id(tkn)['market_data']['low_24h'][self.currency]
            return px
        elif type(self.token_list) == str:
            px = cg_api.get_coin_by_id(self.token_list)['market_data']['low_24h'][self.currency]
            return px

    def px_low( self ):
        return self.low_24h()

    def price_change_24h_in_currency( self ):
        if type(self.token_list) == list:
            px = {}
            for tkn in self.token_list:
                px_change_24h = cg_api.get_coin_by_id(tkn)['market_data']['price_change_24h_in_currency'][self.currency]
                px[tkn]       = px_change_24h
            return px
        elif type(self.token_list) == str:
            px_change_24h = cg_api.get_coin_by_id(self.token_list)['market_data']['price_change_24h_in_currency'][self.currency]
            return px_change_24h

    def px_change_24h( self ):
        return self.price_change_24h_in_currency()

    def total_volume( self ):
        if type(self.token_list) == list:
            px = {}
            for tkn in self.token_list:
                px[tkn] = cg_api.get_coin_by_id(tkn)['market_data']['total_volume'][self.currency]
            return px
        elif type(self.token_list) == str:
            vol = cg_api.get_coin_by_id(self.token_list)['market_data']['total_volume'][self.currency]
            return vol

    def volume( self ):
        return self.total_volume()

    def market_data( self ):
        if type(self.token_list) == list:
            df = pd.DataFrame( index = self.token_list, columns = ['px_last','px_low','px_high','chg_24h','volume'])
            df['px_low'] = pd.Series(self.px_low())
            df['px_high'] = pd.Series(self.px_high())
            df['px_last'] = pd.Series(self.px_last())
            df['chg_24h'] = pd.Series(self.px_change_24h())
            df['volume'] = pd.Series(self.volume())
            final = coin_dict.loc[coin_dict.id.isin(self.token_list)]
        elif type(self.token_list) == str:
            df = pd.DataFrame(index = [self.token_list])
            df['px_last']  = self.px_last()
            df['px_low']   = self.px_low()
            df['px_high']  = self.px_high()
            df['chg_24h'] = self.px_change_24h()
            df['volume']   = self.volume()
            final = coin_dict.loc[coin_dict.id.isin([self.token_list])]
        # Give Name and Symbol
        final = final.set_index("id")
        final = final.join(df,on="id")
        final = final.set_index("symbol")
        del final.index.name
        return final

class HistoricalMarketData:

    def __init__( self, token, currency, start_date, end_date ):
        self.token_list = token
        self.currency   = currency
        start_date      = int(time.mktime(dt.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))
        self.start_date = start_date
        end_date        = int(time.mktime(dt.datetime.strptime(end_date, "%Y-%m-%d").timetuple()))
        self.end_date   = end_date

    def hist_mkt_data( self, feature ):
        if type(self.token_list) == list:
            hist_data = []
            for tkn in self.token_list:
                hist_tkn = cg_api.get_coin_market_chart_range_by_id(tkn,self.currency,self.start_date,self.end_date)[feature]
                hist_tkn = pd.DataFrame(hist_tkn,columns=["date",tkn])
                hist_tkn.date = pd.to_datetime(hist_tkn.date,unit='ms')
                hist_tkn = hist_tkn.set_index("date",True)
                hist_data.append(hist_tkn)
            df_data = pd.concat(hist_data,axis=1)
            del df_data.index.name
            return df_data
        elif type(self.token_list) == str:
            hist_tkn = cg_api.get_coin_market_chart_range_by_id(self.token_list,self.currency,self.start_date,self.end_date)[feature]
            hist_tkn = pd.DataFrame(hist_tkn,columns=["date",self.token_list])
            hist_tkn.date = pd.to_datetime(hist_tkn.date,unit='ms')
            hist_tkn = hist_tkn.set_index("date",True)
            del hist_tkn.index.name
            return hist_tkn

    def price( self ):
        return self.hist_mkt_data( "prices" )

    def volume( self ):
        return self.hist_mkt_data( "total_volumes" )

    def market_cap( self ):
        return self.hist_mkt_data( "market_caps" )

    def all_data( self ):
        if type(self.token_list) == list:
            df1 = self.hist_mkt_data( "prices" )
            df2 = self.hist_mkt_data( "total_volumes" )
            df3 = self.hist_mkt_data( "market_caps" )
            df4 = pd.concat([df1,df2,df3],axis=1)
            cols = [("price",tkn) for tkn in self.token_list] + [("volume",tkn) for tkn in self.token_list] + [("market_cap",tkn) for tkn in self.token_list]
            df4.columns = pd.MultiIndex.from_tuples(cols)
            df4 = df4.swaplevel(i=0, j=1, axis=1)
            df4.sort_index(axis=1, level=0, inplace=True)
            return df4
        elif type(self.token_list) == str:
            df1 = self.hist_mkt_data( "prices" )
            df2 = self.hist_mkt_data( "total_volumes" )
            df3 = self.hist_mkt_data( "market_caps" )
            final = pd.concat([df1,df2,df3],axis=1)
            columns = [(self.token_list,'price'),(self.token_list,'volume'),(self.token_list,'market_cap')]
            final.columns = pd.MultiIndex.from_tuples(columns)
            return final
