import numpy as np

# Persistent history list (acts like internal memory)
history = []

def reset_history():
    """Clears stored price history."""
    global history
    history = []

def is_outlier(price, window=20, threshold=3):
    """
    Determines if the incoming price is an outlier based on rolling Z-score.
    """
    global history

    # Need enough data to compute rolling stats
    if len(history) < 5:
        return False

    window_slice = np.array(history[-window:])
    mean = np.mean(window_slice)
    std = np.std(window_slice)

    if std == 0:
        return False

    z = abs(price - mean) / std
    return z > threshold

def clean_price(price, window=20, threshold=3):
    """
    Cleans the incoming price:
    - If it's an outlier → replace with rolling mean
    - Otherwise → keep original
    """
    global history

    if is_outlier(price, window, threshold):
        window_slice = np.array(history[-window:])
        cleaned = float(np.mean(window_slice))
    else:
        cleaned = price

    history.append(cleaned)
    return cleaned
