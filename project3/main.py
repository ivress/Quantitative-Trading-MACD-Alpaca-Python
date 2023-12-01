import alpaca_trade_api as tradeapi
from Trading_engine import TradingEngine
import yaml

def main():
    
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    API_KEY = config["api_key"]
    API_SECRET = config["api_secret"]
    BASE_URL = config["base_url"]

    
    api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL)

    
    symbol = "AAPL"

    
    engine = TradingEngine(api, symbol)

    
    engine.run()

if __name__ == "__main__":
    main()
