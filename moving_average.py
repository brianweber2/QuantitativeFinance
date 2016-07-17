# Import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


security = 'RMTI'
rmti_daily_close = get_pricing(
    security,
    fields='close_price', # modify to price, open_price, high, low or volume to change the field
    start_date='2012-01-01', # Customize your pricing date range
    end_date='2016-07-04',
    frequency='daily', # change to minute for minute pricing
)

pricing = get_pricing(
    security, 
    start_date='2012-01-01', 
    end_date='2016-07-04', 
    frequency='daily'
)
pricing_open = pricing['open_price']
pricing_open = pricing.open_price
pricing_open.head()

# Plot price
plt.title('RMTI Close Price')
plt.xlabel('Time')
plt.ylabel('Close Price ($)')
rmti_daily_close.plot() # same as plt.plot(rmti_daily_close)

# Let's add moving averages to the plot
MA_20 = pd.rolling_mean(rmti_daily_close, window=20)
MA_50 = pd.rolling_mean(rmti_daily_close, window=50)
MA_200 = pd.rolling_mean(rmti_daily_close, window=200)

# Plot price w/ moving averages
plt.plot(rmti_daily_close.index, rmti_daily_close.values) # same as rmti_daily_close.plot()
plt.plot(MA_20.index, MA_20.values)
plt.plot(MA_50.index, MA_50.values)
plt.plot(MA_200.index, MA_200.values, 'y')
plt.title('RMTI Close Price')
plt.xlabel('Time')
plt.ylabel('Close Price ($)')
plt.legend(['RMTI','20 Day MA','50 Day MA', '200 Day MA'])