
# Exchange Connection

Contains the connection to the AWS services to retrieve the historical data.
The data is automatically saved every 10 minutes to create the historical.


## Usage

Deploy using serverless framwework

```python
# Get the last 30 minutes
tickers = ConnectBitso.fetch_last_thirty_minutes(ConnectBitso)
btc_mxn_ticker = BtcMxnTicker(tickers[0])
print(tickers)

# Gets last 100 historical data using epoch
tickers = ConnectBitso.fetch_by_epoch(ConnectBitso, 0, 1620433700)
btc_mxn_ticker = BtcMxnTicker(tickers[0])
print(tickers)
```


## Contributing
Fork the project.
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.


# Attention
The AWS URL path for the service is private, DO NOT publish the URL, please.
Ask for the URL, and it shall be given.
Thanks for your understanding. Happy coding!

