import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

def get_stock_data(ticker, start, end):
    stock = yf.download(ticker, start=start, end=end)
    if stock.empty:
        print(f"No data found for {ticker}.")
        return None
    print(stock)  
    return stock

def calculate_technical_indicators(df):
    if df is None:
        return None
    
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband(), \
                                                      ta.volatility.BollingerBands(df['Close']).bollinger_mavg(), \
                                                      ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    return df

def moving_average_crossover_strategy(df):
    if df is None:
        return None
    
    
    df['Signal_MA'] = 0
    df['Signal_RSI'] = 0
    df['Signal_BB'] = 0

   
    df.loc[df['SMA_50'] > df['SMA_200'], 'Signal_MA'] = 1 
    df.loc[df['SMA_50'] < df['SMA_200'], 'Signal_MA'] = -1  

    # RSI based buy/sell signals
    df.loc[df['RSI'] < 30, 'Signal_RSI'] = 1  
    df.loc[df['RSI'] > 70, 'Signal_RSI'] = -1 

    # Bollinger Bands based buy/sell signals
    df.loc[df['Close'] < df['BB_lower'], 'Signal_BB'] = 1 
    df.loc[df['Close'] > df['BB_upper'], 'Signal_BB'] = -1  

    # Combine all signals: You can tweak the logic here
    df['Signal'] = df[['Signal_MA', 'Signal_RSI', 'Signal_BB']].mean(axis=1)

    # Convert combined signal to buy/sell/hold:
    df['Final_Signal'] = 0
    df.loc[df['Signal'] > 0, 'Final_Signal'] = 1  # Buy
    df.loc[df['Signal'] < 0, 'Final_Signal'] = -1  # Sell

    return df

def plot_stock(df, ticker):
    if df is None:
        print(f"No data available to plot for {ticker}.")
        return
    
    plt.figure(figsize=(14, 7))
    plt.plot(df['Close'], label=f'{ticker} Close Price', color='blue')
    plt.plot(df['SMA_50'], label='50-Day SMA', color='green')
    plt.plot(df['SMA_200'], label='200-Day SMA', color='red')
    plt.fill_between(df.index, df['BB_lower'], df['BB_upper'], color='gray', alpha=0.2, label='Bollinger Bands')

    plt.title(f'{ticker} Stock Price with Indicators')
    plt.xlabel('Date')
    plt.ylabel('Price')

    signal_sum = df['Final_Signal'].sum()

    if signal_sum > 0:
        recommendation = "Buy"
        color = 'green'
    elif signal_sum < 0:
        recommendation = "Sell"
        color = 'red'
    else:
        recommendation = "Hold"
        color = 'orange'

    plt.text(df.index[-1], df['Close'].iloc[-1], recommendation, color=color, fontsize=15, weight='bold')

    plt.legend()
    plt.show()


ticker = 'BTC-USD'
start_date = '2023-10-01'
end_date = '2024-10-01'


stock_data = get_stock_data(ticker, start=start_date, end=end_date)


stock_data = calculate_technical_indicators(stock_data)

stock_data = moving_average_crossover_strategy(stock_data)

if stock_data is not None:
    plot_stock(stock_data, ticker)
else:
    print(f"No stock data available for {ticker}.")
