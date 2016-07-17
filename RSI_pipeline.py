# Import required libraries

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from quantopian.pipeline import Pipeline
from quantopian.research import run_pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage, AverageDollarVolume, RSI
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.filters.morningstar import IsPrimaryShare



# Create function to make Pipeline

# Pipeline criteria
#
#  Is a primary share
#  Is listed as a common stock
#  Is not a depositary receipt (ADR/GDR)
#  Is not trading over-the-counter (OTC)
#  Is not when-issued (WI)
#  Doesn't have a name indicating it's a limited partnership (LP)
#  Doesn't have a company reference entry indicating it's a LP
#  Calculate RSI for a window_length of 14 days; RSI values >= 70 go short; <= 30 go long
#  Average daily volume for the past 30 days is at least 1,000,000


def make_pipeline():
    
    # Is a primary share
    is_primary_share = IsPrimaryShare()
    
    # Is listed as a common stock
    is_common_stock = morningstar.share_class_reference.security_type.latest.eq('ST00000001')
    
    # Is not a depositary receipt (ADR/GDR)
    not_depositary = ~morningstar.share_class_reference.is_depositary_receipt.latest
    
    # Is not trading over-the-counter (OTC)
    not_otc = ~morningstar.share_class_reference.exchange_id.latest.startswith('OTC')
    
    # Is not when-issued (WI)
    not_wi = ~morningstar.share_class_reference.symbol.latest.endswith('.WI')
    
    # Doesn't have a name indicating it's a limited partnership (LP)
    not_lp_name = ~morningstar.company_reference.standard_name.latest.matches('.* L[. ]?P.?$')
    
    # Doesn't have a company reference entry indicating it's a LP
    not_lp_balance_sheet = morningstar.balance_sheet.limited_partnership.latest.isnull()
    
    # Average daily dollar volume for the past 30 days is at least $10,000,000
    dollar_volume = AverageDollarVolume(window_length=30)
    high_dollar_volume = dollar_volume > 1e7
    
    # Not a penny stock
    above_5 = USEquityPricing.close.latest > 5
    
    # Combine filters into a variable for masking
    base_universe = (
        is_primary_share
        & is_common_stock
        & not_depositary
        & not_otc
        & not_wi
        & not_lp_name
        & not_lp_balance_sheet
        & high_dollar_volume
        & above_5
    )
    
    # Calculate RSI for a window_length of 14 days; RSI values >= 70 go short; <= 30 go long
    rsi_14_days = RSI(window_length=14, mask=base_universe)
    
    rsi_long = rsi_14_days <= 30
    rsi_short = rsi_14_days >= 70
    
    rsi_long_stocks = RSI(window_length=14, mask=base_universe).bottom(10)
    rsi_short_stocks = RSI(window_length=14, mask=base_universe).top(10)
    
    securities_to_trade = (rsi_long_stocks | rsi_short_stocks)    
        
    # Need to calculate the momentum change in the RSI values from previous day. The idea is that
    # the greater difference in the RSI value from the previous day, the more likely the stock is
    # to continue in that direction. If the difference is a large positive number, we want to change 
    # our short positions to long, and keep our long positions. The exact opposite if we have a 
    # large negative number. Take the top 10% from the longs and shorts.
    
    
    # return pipeline with factor, filter and classifier desired
    return Pipeline(
        columns={
            'RSI': rsi_14_days,
            'Short': rsi_short,
            'Long': rsi_long,
        },
        screen=securities_to_trade
    )