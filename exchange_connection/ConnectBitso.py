import json

import requests

# Global variables
aws_url = ''


# Class to connect to AWS service endpoint
class ConnectBitso:

    # Gets the last thirty minutes from the services
    # Returns an array of objects in ascending order
    def fetch_last_thirty_minutes(self):
        response = requests.get(aws_url + '/get_historical_tickers')
        tickers_response = response.json()
        return tickers_response['items']

    # Gets the top 100 records according to epoch
    # Returns an array of objects in ascending order
    def fetch_by_epoch(self, low_value, high_value):
        payload = {'low_value': low_value, 'high_value': high_value}
        response = requests.get(aws_url + '/get_historical_tickers',
                                params=payload)
        tickers_response = response.json()
        return tickers_response['items']

    def fetch_account_balance(self):
        response = requests.get(aws_url + '/get_balance')
        balance_response = response.json()
        return balance_response

    def post_order(self, order):
        response = requests.post(aws_url + '/post_order', json=order.to_json())
        order_response = response.json()
        return order_response['oid']

    def cancel_order(self, oid):
        response = requests.delete(aws_url + '/cancel_order/' + oid)
        cancellation_response = response.content
        return cancellation_response

# Order to be sent to Bitso
class RawOrder(object):
    def __init__(self, btc_price, mxn_price, side, time_in_force, order_type, instrument):
        self.book = 'btc_mxn'  # Specifies which book to use ('btc_mxn' only)
        self.btc_price = btc_price  # BTC price
        self.mxn_price = mxn_price  # MXN price
        self.side = side  # The order side (buy, sell)
        self.time_in_force = time_in_force  # Indicates how long a limit order will remain active
        # before it is executed or expires (goodtillcancelled, fillorkill, immediateorcancel, postonly)
        self.order_type = order_type  # The order type (market, limit)
        self.instrument = instrument  # When buying at market price, sets the currency to buy ('mxn' or 'btc' only)

    # Parse the object to a json format to be post
    def to_json(self):
        json = {
            "book": self.book,
            "btc_price": self.btc_price,
            "mxn_price": self.mxn_price,
            "side": self.side,
            "time_in_force": self.time_in_force,
            "order_type": self.order_type,
            "instrument": self.instrument
        }
        return json


# Bitso balance, containing a list of currencies and a list of open orders
class BtcMxnBalance(object):
    def __init__(self):
        self.account_balance = []
        self.account_orders = []

    def addCryptoBalance(self, currency):
        self.account_balance.append(currency)

    def addOrder(self, order):
        self.account_orders.append(order)


# Currency balance in Bitso Account
class Currency(object):
    def __init__(self, currency):
        self.currency = currency['currency']  # Currency symbol
        self.available = currency['available']  # Currency balance available for use
        self.locked = currency['locked']  # Currency balance locked in open orders
        self.total = currency['total']  # Total balance
        self.pending_deposit = currency['pending_deposit']
        self.pending_withdrawal = currency['pending_withdrawal']


# Open orders in Bitso Account
class AccountOrder(object):
    def __init__(self, order):
        self.original_value = order['original_value']  # The order’s initial minor currency amount
        self.unfilled_amount = order['unfilled_amount']  # The order’s unfilled major currency amount
        self.original_amount = order['original_amount']  # The order’s initial major currency amount
        self.book = order['book']  # Order book symbol
        self.created_at = order['created_at']  # Timestamp at which the trade was executed
        self.updated_at = order['updated_at']  # Timestamp at which the trade was updated (can be null)
        self.price = order['price']  # The order’s price
        self.side = order['side']  # The order side (buy, sell)
        self.type = order['type']  # The order type (will always be 'limit’ for open orders)
        self.oid = order['oid']  # The Order ID
        self.status = order['status']  # The order’s status (queued, open, partial-fill)
        self.time_in_force = order['time_in_force']  # Indicates how long a limit order will remain active before
        # (goodtillcancelled, fillorkill, immediateorcancel, postonly)


# Ticker object according to Bitso response:
# https://bitso.com/developers#ticker
class BtcMxnTicker(object):
    def __init__(self, ticker):
        self.book = ticker['book']  # Order book symbol
        self.volume = ticker['volume']  # Last 24 hours volume
        self.high = ticker['high']  # Last 24 hours price high
        self.last = ticker['last']  # Last traded price
        self.low = ticker['low']  # Last 24 hours price low
        self.vwap = ticker['vwap']  # Last 24 hours volume weighted average price:
        # https://en.wikipedia.org/wiki/Volume-weighted_average_price
        self.ask = ticker['ask']  # Lowest sell order
        self.bid = ticker['bid']  # Highest buy order
        self.created_at = ticker['created_at']  # Timestamp at which the ticker was generated
        self.epoch_datetime = ticker['epoch_datetime']  # 'created_at' in epoch
        self.change_24 = ticker['change_24']  # Unknown. Not present on Bitso API documentation
