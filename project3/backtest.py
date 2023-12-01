import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
from datetime import datetime
import yaml
import matplotlib.pyplot as plt

class BacktestEngine:
    def __init__(self, api, symbol, start_date, end_date):
        self.api = api
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def get_historical_data(self):
        df = self.api.get_bars(self.symbol,TimeFrame.Day, start=self.start_date, end=self.end_date).df
        return df

    def calculate_macd(self, df, slow=26, fast=12, signal=9):
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        return df

    def simulate_trades(self, df):
        
        balance = 100000
        position = 0
        trade_logs = []

        for index, row in df.iterrows():
            if row['macd'] > row['signal'] and position == 0:
                
                position = balance / row['close']
                balance = 0
                trade_logs.append((index, 'buy', row['close'], position))

            elif row['macd'] < row['signal'] and position > 0:
                
                balance = position * row['close']
                position = 0
                trade_logs.append((index, 'sell', row['close'], balance))

        return trade_logs

    def run_backtest(self):
        df = self.get_historical_data()
        df = self.calculate_macd(df)
        trade_logs = self.simulate_trades(df)
        return trade_logs
    
    def plot_performance(self, trade_logs, df):

        account_value = [100000]

        last_val = account_value[0]
        trade_log_iter = iter(trade_logs)
        current_trade = next(trade_log_iter, None)


        for date in df.index:
            if current_trade and date == current_trade[0]:

                last_val = current_trade[3] if current_trade[1] == 'sell' else last_val
                current_trade = next(trade_log_iter, None)
            account_value.append(last_val)


        df['benchmark'] = df['close'] / df['close'].iloc[0] * account_value[0]


        plt.figure(figsize=(12, 6))
        plt.plot(df.index, account_value[1:], label='Strategy Performance')
        plt.plot(df.index, df['benchmark'], label='Benchmark Performance')
        plt.title('Strategy vs. Benchmark Performance')
        plt.xlabel('Date')
        plt.ylabel('Account Value')
        plt.legend()
        plt.show()



def main():
    
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    API_KEY = config["api_key"]
    API_SECRET = config["api_secret"]
    BASE_URL = config["base_url"]

    api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL)
    symbol = "AAPL"
    start_date = '2019-01-01'
    end_date = '2023-01-01'

    backtest_engine = BacktestEngine(api, symbol, start_date, end_date)
    trade_logs = backtest_engine.run_backtest()

    df_with_macd = backtest_engine.get_historical_data()
    df_with_macd = backtest_engine.calculate_macd(df_with_macd)

    backtest_engine.plot_performance(trade_logs, df_with_macd)

    for log in trade_logs:
        print(log)

if __name__ == "__main__":
    main()
