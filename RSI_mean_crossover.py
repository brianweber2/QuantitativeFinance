
"""
This algorithm calculates the Relative Strength Index (RSI) for one stock over
a specified window length. The mean and weighted mean (exponential moving average)
are calculated. The weighted mean is compared with the actual RSI value of the stock
to determine when a RSI crossover occurs.
"""

import numpy as np
import pandas as pd
import talib

# Setup our variables
def initialize(context):
    context.stock = sid(18196) # stock that I want to backtest
    context.LOW_RSI = 30
    context.HIGH_RSI = 70
    
    # Rebalance every day, 30 minutes hour after market open on Monday.
    schedule_function(my_rebalance,
                      date_rules.every_day(),
                      time_rules.market_open(minutes=30))
     
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, 
                      date_rules.every_day(), 
                      time_rules.market_close())
    
     
def my_rebalance(context, data):
    # Window length
    window = 9
    
    # Load historical data for the stock
    hist = data.history(context.stock, 'price', 20, '1d')
    
    # Calculate RSI moving average
    rsi = talib.RSI(hist, timeperiod=window)
    context.rsi_current = rsi[-1] # Get most recent RSI of the stock
    context.rsi_mean = np.nanmean(rsi) 
    
    # Calculate RSI EWMA
    center_of_mass = (window - 1) / 2
    context.rsi_ewma = pd.ewma(rsi, com=center_of_mass, ignore_na=True)
    
    # Calculate rsi moving average crossover
    rsi_crossover = context.rsi_current - context.rsi_ewma[-1]
    
    # Get current price for today
    context.current_price = data.history(context.stock, 'price', 1, '1d')
    
    current_position = context.portfolio.positions[context.stock].amount
    
    # RSI > RSI_mean (long position)
    if rsi_crossover > 0 and data.can_trade(context.stock):
        log.info("Long position.")
        order_target_percent(context.stock, 1)        
    # RSI < RSI_mean (short position)
    elif rsi_crossover < 0 and data.can_trade(context.stock):
        log.info("Short position.")
        order_target_percent(context.stock, -1)
    
 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    
    record(
        stock_rsi=context.rsi_current,
        # stock_rsi_avg=context.rsi_mean,
        stock_rsi_ewma=context.rsi_ewma[-1],
        stock_price=context.current_price
    )