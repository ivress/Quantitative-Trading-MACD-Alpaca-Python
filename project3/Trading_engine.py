import alpaca_trade_api as tradeapi
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import logging

logging.basicConfig(filename='trading_engine.log', level=logging.INFO)

class TradingEngine:

    def __init__(self, api, symbol):
        self.api = api
        self.symbol = symbol

    def get_historical_data(self, start_date, end_date):
        df = self.api.get_bars(self.symbol, 'day', start=start_date, end=end_date).df
        return df

    def calculate_macd(self, df, slow=26, fast=12, signal=9):
        
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        
        return df

    def trade_logic(self,start_date, end_date):
        
        historical_data = self.get_historical_data(start_date, end_date)
        df = self.calculate_macd(historical_data)
        last_row = df.iloc[-1]
        
        balance = 10000
        trade_quantity = balance / last_row['close']

        if last_row['macd'] > last_row['signal']:
            
            try:
                self.api.submit_order(
                    symbol=self.symbol,
                    qty=trade_quantity,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                logging.info(f"Executed buy order for {trade_quantity} shares of {self.symbol} on {last_row.name}")
            except Exception as e:
                logging.error(f"Error executing buy order: {e}")

        elif last_row['macd'] < last_row['signal']:
            
            try:
                position = self.api.get_position(self.symbol)
                position_qty = float(position.qty)

                
                if position_qty > 0:
                    self.api.submit_order(
                        symbol=self.symbol,
                        qty=position_qty,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                    logging.info(f"Executed sell order for {position_qty} shares of {self.symbol} on {last_row.name}")
            except Exception as e:
                logging.error(f"Error executing sell order: {e}")
            

    def run(self):

        start_date = '2021-01-01'
        end_date = datetime.now().strftime('%Y-%m-%d')
        df = self.get_historical_data(start_date, end_date)

        df = self.calculate_macd(df)

        self.trade_logic(start_date, end_date)

        