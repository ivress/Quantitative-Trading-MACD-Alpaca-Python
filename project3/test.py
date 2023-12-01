from alpaca_trade_api.rest import REST, TimeFrame
import alpaca_trade_api as tradeapi
from datetime import datetime
import yaml

# We use Alpaca API get_bars function to obtain target stock market data and save it into target folder with specific filename

# Set API key and secret

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

API_KEY = config["api_key"]
API_SECRET = config["api_secret"]
BASE_URL = config["base_url"]

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

tickers = 'AAPL'
start_time = '2022-11-01'
end_time =  '2023-11-01'

data_bar = api.get_bars(tickers,TimeFrame.Day, start=start_time, end=end_time, adjustment='raw').df

print(data_bar)