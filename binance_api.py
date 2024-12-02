import os
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()

class BinanceAPI:
    def __init__(self, date_type):
        self.api_key = os.getenv("BINANCE_API_KEY")  # Load your API key from environment variables
        self.secret_key = os.getenv("BINANCE_API_SECRET")  # Load your secret key from environment variables
        self.date_type = date_type
        
        if not self.api_key:
            raise ValueError("API Key required for private endpoints")
        if not self.secret_key:
            raise ValueError("API Secret required for private endpoints")
        
        self.client = Client(self.api_key, self.secret_key)  # Initialize the Binance client
        self.client.API_URL = "https://api.binance.com"
        self.skipped_symbols = []

    def get_margin_account(self):
        # Fetch margin account information using the python-binance library
        margin_info = self.client.get_margin_account()
        return margin_info  # Return the margin account information
    
    def get_cross_trades(self, symbol):
        try:
            trades = self.client.get_margin_trades(symbol=f"{symbol}USDT")
            return trades
        except Exception as e:
            self.skipped_symbols.append(symbol)
            return None  # Return None or an empty list based on your preference
        
    def get_week_dates(self):
        today = datetime.now().date()
        week_dates = [today - timedelta(days=x) for x in range(7)]
        return week_dates
    
    def get_current_month_dates(self):
        today = datetime.now().date()
        first_day_of_month = today.replace(day=1)  # Get the first day of the current month
        month_dates = [first_day_of_month + timedelta(days=x) for x in range((today - first_day_of_month).days + 1)]
        return month_dates  # Return dates for the current month

    def get_last_month_dates(self):
        today = datetime.now().date()
        first_day_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)  # Get the first day of the last month
        last_month_dates = [first_day_of_last_month + timedelta(days=x) for x in range((today - first_day_of_last_month).days + 1)]
        return last_month_dates  # Return dates for the last month
    
    def get_recent_trades(self, trades):
        from datetime import datetime
        
        if self.date_type == "day": 
            today = datetime.now().date()  # Get today's date
            today_trades = [trade for trade in trades if datetime.fromtimestamp(trade['time'] / 1000).date() == today]
            return today_trades  # Return trades that occurred today
        elif self.date_type == "week":
            week_trades = [trade for trade in trades if datetime.fromtimestamp(trade['time'] / 1000).date() in self.get_week_dates()]
            return week_trades  # Return trades that occurred this week
        elif self.date_type == "tmonth":
            month_trades = [trade for trade in trades if datetime.fromtimestamp(trade['time'] / 1000).date() in self.get_current_month_dates()]
            return month_trades  # Return trades that occurred this month
        elif self.date_type == "lmonth":
            last_month_trades = [trade for trade in trades if datetime.fromtimestamp(trade['time'] / 1000).date() in self.get_last_month_dates()]
            return last_month_trades  # Return trades that occurred last month

    def analyze_trades(self, trades):
        total_profit_loss = 0.0
        win_count = 0
        loss_count = 0

        for trade in trades:
            # Assuming trades have 'profit' key for profit/loss calculation
            profit = trade.get('profit', 0.0)  # Replace with actual profit calculation if needed
            total_profit_loss += profit
            
            if profit > 0:
                win_count += 1
            elif profit < 0:
                loss_count += 1

        total_trades = win_count + loss_count
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0

        return {
            "total_profit_loss": total_profit_loss,
            "win_rate": win_rate,
            "total_trades": total_trades
        }
        
    def get_skipped_symbols(self):
        return self.skipped_symbols