# signals.py
"""
Simple signal generators used by the Streamlit UI.

- momentum(prices, window): price_now - price_window_ago
- rolling_volatility(prices, window): std of the last window prices
- moving_average(prices, window): simple moving average
- vwap(prices, volumes, window): volume-weighted average price over window
"""

import numpy as np

def momentum(prices, window=3):
    if len(prices) < window:
        return None
    return prices[-1] - prices[-window]

def rolling_volatility(prices, window=20):
    if len(prices) < window:
        return None
    return float(np.std(prices[-window:]))

def moving_average(prices, window=5):
    if len(prices) < window:
        return None
    return float(np.mean(prices[-window:]))

def vwap(prices, volumes, window=20):
    if len(prices) < window:
        return None
    p = np.array(prices[-window:])
    v = np.array(volumes[-window:])
    denom = v.sum()
    if denom == 0:
        return None
    return float((p * v).sum() / denom)
