# Binance Margin Tracker

## Overview
The Binance Margin Tracker is a Python application that allows users to track their margin account information, view recent trades, and analyze trading performance using the Binance API. It provides a user-friendly console interface with rich formatting.

## Features
- Display margin account information
- View recent trades
- Analyze trading performance (total profit/loss, win rate)
- Change the data interval (day, week, month)

## Requirements
- Python 3.7 or higher
- Required Python packages listed in `requirements.txt`

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kenguru10/binance_margin_tracker.git
   cd binance_margin_tracker
   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Binance API credentials:**
   Ensure you have your Binance API key and secret. You may need to modify the `binance_api.py` file to include your credentials.

## Usage

1. **Run the application:**
   ```bash
   python binance_tracker.py
   ```

2. **Select an option from the menu:**
   - **1. Display margin account info**: Fetch and display your margin account information.
   - **2. Display recent trades**: Fetch and display your recent trades.
   - **3. Display trade analysis**: Analyze your trading performance.
   - **4. Change interval**: Change the data interval for fetching trades (e.g., 'day', 'week', 'month').
   - **5. Exit**: Exit the application.

## Notes
- Ensure that your Binance account has margin trading enabled.
- The application uses the `rich` library for console output, which provides a better user experience.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Feel free to submit issues or pull requests if you have suggestions or improvements!

## Acknowledgments
- [Binance API](https://binance-docs.github.io/apidocs/spot/en/)
- [Rich](https://rich.readthedocs.io/en/stable/)