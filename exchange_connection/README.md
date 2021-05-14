
# Exchange Connection

ConnectBitso is a class to reach the exchange service. You can get historical data, get the current account and post orders.


## Usage

```python
# Get the last 30 minutes
tickers = ConnectBitso.fetch_last_thirty_minutes(ConnectBitso)
btc_mxn_ticker = BtcMxnTicker(tickers[0])
print(tickers)

# Gets last 100 historical data using epoch
tickers = ConnectBitso.fetch_by_epoch(ConnectBitso, 0, 1620433700)
btc_mxn_ticker = BtcMxnTicker(tickers[0])
print(tickers)

# Create a new order
order = SendOrder('1.0000', '500', 'buy', 'goodtillcancelled', 'limit', '')
print(order.to_json())
# Post the order to the exchange service
new_order = ConnectBitso.post_order(ConnectBitso, order)
print(new_order)

# Gets the account balance
balance = ConnectBitso.fetch_account_balance(ConnectBitso)
print(balance)

# Cancel order
# The oid should be saved previously. It's returned by the post_order method
cancellation = ConnectBitso.cancel_order(ConnectBitso, 'oid')
print(cancellation)
```


## Contributing
Fork the project.
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.


# Attention
The AWS URL path for the service is private, DO NOT publish the URL, please.
Ask for the URL, and it shall be given.
Thanks for your understanding. Happy coding!

