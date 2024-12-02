import os
import json
from datetime import datetime
from binance_api import BinanceAPI
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

class BinanceMarginTracker:
    def __init__(self, date_type):
        self.api = BinanceAPI(date_type)  # Initialize your Binance API client
        self.console = Console()  # Initialize rich console for better UI
        self.date_type = date_type

    def get_margin_account_info(self):
        # Fetch margin account information
        margin_info = self.api.get_margin_account()
        return margin_info

    def display_margin_info(self, margin_info):
        # Create a table to display margin account information
        table = Table(title="Margin Account Information")
        table.add_column("Asset", justify="left", style="cyan")
        table.add_column("Free", justify="right", style="magenta")
        table.add_column("Locked", justify="right", style="yellow")
        table.add_column("Total", justify="right", style="green")

        for asset in margin_info['userAssets']:
            free_amount = float(asset['free'])
            locked_amount = float(asset['locked'])
            total_amount = free_amount + locked_amount
            
            # Only display assets that have a non-zero balance
            if total_amount > 0:
                table.add_row(
                    asset['asset'],
                    str(free_amount),
                    str(locked_amount),
                    str(total_amount)
                )

        self.console.print(table)

    def get_all_coins(self, margin_info):
        coins = [asset['asset'] for asset in margin_info['userAssets']]
        return coins
    
    def get_all_cross_trades(self, coins, progress=None):
        all_trades = []
        if progress:
            task = progress.add_task(f"[cyan]Fetching cross trades for {len(coins)} coins...", total=len(coins))
            for index, coin in enumerate(coins):
                trades = self.api.get_cross_trades(coin)
                if trades and len(trades) > 0:
                    all_trades.extend(trades)
                progress.update(task, description=f"[cyan]Fetching cross trades: {index + 1}/{len(coins)}")  # Update description with current count
                progress.advance(task)
            progress.remove_task(task)  # Clear the fetching text after loading
        else:
            for coin in coins:
                trades = self.api.get_cross_trades(coin)
                if trades and len(trades) > 0:
                    all_trades.extend(trades)
        return all_trades

    def display_recent_trades(self, recent_trades):
        self.console.print(f"{self.date_type} Summary")
        # Create a table to display recent trades
        table = Table(title="Recent Trades")
        table.add_column("Symbol", justify="left", style="cyan")
        table.add_column("Price", justify="right", style="magenta")
        table.add_column("Quantity", justify="right", style="yellow")
        table.add_column("Time", justify="right", style="green")
        table.add_column("Result", justify="center", style="blue")

        # Group trades by symbol
        trades_by_symbol = {}
        for trade in recent_trades:
            symbol = trade['symbol']
            if symbol not in trades_by_symbol:
                trades_by_symbol[symbol] = []
            trades_by_symbol[symbol].append(trade)

        # Calculate results for the most recent two trades of each symbol
        for symbol, trades in trades_by_symbol.items():
            # Sort trades by time (latest to oldest)
            trades.sort(key=lambda trade: trade['time'], reverse=True)

            # Check the most recent two trades
            if len(trades) >= 2:
                latest_trade = trades[0]
                previous_trade = trades[1]
                
                # Convert prices to float for calculation
                latest_price = float(latest_trade['price'])
                previous_price = float(previous_trade['price'])
                
                price_change = latest_price - previous_price
                result = "Gain" if price_change > 0 else "Loss" if price_change < 0 else "No Change"
            else:
                # If there's only one trade, we can't determine gain/loss
                result = "N/A"

            # Add the most recent trade to the table
            table.add_row(
                latest_trade['symbol'],
                str(latest_trade['price']),
                str(latest_trade['qty']),
                datetime.fromtimestamp(latest_trade['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                result
            )

        self.console.print(table)

    def display_trade_analysis(self, recent_trades):
        # Calculate total profit/loss and win rate from trades
        total_profit_loss = 0
        total_investment = 0  # Initialize total investment
        winning_trades = 0
        total_trades = len(recent_trades) // 2  # Divide total trades by 2
        
        # Group trades by symbol
        trades_by_symbol = {}
        for trade in recent_trades:
            symbol = trade['symbol']
            if symbol not in trades_by_symbol:
                trades_by_symbol[symbol] = []
            trades_by_symbol[symbol].append(trade)
        
        # Calculate metrics for each symbol
        for symbol, trades in trades_by_symbol.items():
            # Sort trades by time (oldest to newest)
            trades.sort(key=lambda x: x['time'])
            
            # Compare consecutive trades
            for i in range(1, len(trades)):
                prev_price = float(trades[i-1]['price'])
                curr_price = float(trades[i]['price'])
                quantity = float(trades[i]['qty'])
                
                # Calculate profit/loss for this trade
                trade_pl = (curr_price - prev_price) * quantity
                total_profit_loss += trade_pl
                total_investment += prev_price * quantity  # Update total investment
                
                if trade_pl > 0:
                    winning_trades += 1
        
        # Calculate win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate profit/loss percentage
        profit_loss_percentage = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0  # Calculate percentage
        
        # Display results
        self.console.print(f"Total Profit/Loss: {total_profit_loss:.2f}")
        self.console.print(f"Profit/Loss Percentage: {profit_loss_percentage:.2f}%")  # Display percentage
        self.console.print(f"Win Rate: {win_rate:.2f}%")
        self.console.print(f"Total Trades: {total_trades}")
        self.console.print(f"Skipped Symbols: {self.api.get_skipped_symbols()}")

    def run(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Fetch margin account info
            task1 = progress.add_task("[cyan]Fetching margin account info...", total=1)
            margin_info = self.get_margin_account_info()
            progress.update(task1, completed=1.0)
            progress.remove_task(task1)  # Clear the fetching text after loading

            self.display_margin_info(margin_info)
            
            # Fetch and process trades
            task2 = progress.add_task("[cyan]Processing trades...", total=2)  # Total steps for processing trades
            coins = self.get_all_coins(margin_info)
            progress.update(task2, completed=0.5)  # Update to 50% after fetching coins
            all_trades = self.get_all_cross_trades(coins, progress)
            recent_trades = self.api.get_recent_trades(all_trades)
            progress.update(task2, completed=1.0)  # Complete the task
            progress.remove_task(task2)  # Clear the fetching text after loading
            
            # Sort and display results
            recent_trades.sort(key=lambda trade: trade['time'], reverse=True)
            self.display_recent_trades(recent_trades)
            self.display_trade_analysis(recent_trades)

if __name__ == "__main__":
    tracker = BinanceMarginTracker("week")
    tracker.run()
