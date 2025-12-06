import numpy as np

class ZScoreCleaner:
    """
    Rolling Z-score based spike/outlier cleaner.
    If |price - mean| / std > threshold, replace with rolling mean.
    """

    def __init__(self, window=20, threshold=3):
        self.window = window
        self.threshold = threshold
        self.history = []

    def reset(self):
        self.history = []

    def is_outlier(self, price):
        if len(self.history) < 5:
            return False

        window_slice = np.array(self.history[-self.window:])
        mean = np.mean(window_slice)
        std = np.std(window_slice)

        if std == 0:
            return False

        z = abs(price - mean) / std
        return z > self.threshold

    def clean(self, price):
        if self.is_outlier(price):
            window_slice = np.array(self.history[-self.window:])
            cleaned = float(np.mean(window_slice))
        else:
            cleaned = price

        self.history.append(cleaned)
        return cleaned
