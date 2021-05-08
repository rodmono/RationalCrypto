import requests

# Global variables
aws_url = ''


# Class to connect to AWS service endpoint
class ConnectBitso:

    # Gets the last thirty minutes from the services
    # Returns an array of objects in ascending order
    def fetch_last_thirty_minutes(self):
        response = requests.get(aws_url)
        tickers_response = response.json()
        return tickers_response['items']

    # Gets the top 100 records according to epoch
    # Returns an array of objects in ascending order
    def fetch_by_epoch(self, low_value, high_value):
        payload = {'low_value': low_value, 'high_value': high_value}
        response = requests.get(aws_url, params=payload)
        tickers_response = response.json()
        return tickers_response['items']

# Ticker object according to Bitso response:
# https://bitso.com/developers#ticker
class BtcMxnTicker(object):
    def __init__(self, ticker):
        self.book = ticker['book']  # Order book symbol
        self.volume = ticker['volume']  # Last 24 hours volume
        self.high = ticker['high']  # Last 24 hours price high
        self.last = ticker['last']  # Last traded price
        self.low = ticker['low']  # Last 24 hours price low
        self.vwap = ticker['vwap']  # Last 24 hours volume weighted average price: https://en.wikipedia.org/wiki/Volume-weighted_average_price
        self.ask = ticker['ask']  # Lowest sell order
        self.bid = ticker['bid']  # Highest buy order
        self.created_at = ticker['created_at']  # Timestamp at which the ticker was generated
        self.epoch_datetime = ticker['epoch_datetime']  # 'created_at' in epoch
        self.change_24 = ticker['change_24']  # Unknown. Not present on Bitso API documentation
