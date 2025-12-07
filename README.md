# Data Cleaning Pipeline using Z-Test

Python-based pipeline to automatically detect and remove outliers from datasets using the Z-Test statistical method.
This project is designed for data preprocessing, anomaly detection, and ensuring clean input data for machine learning or analytics pipelines.

## Features

- 📥 CSV ingestion
- 🧹 Automatic data cleaning using Z-Scores
- 📈 Outlier detection on numerical columns
- 🗑️ Configurable threshold (default = 3 standard deviations)
- 📤 Exports cleaned dataset
- 🧪 Reports number of removed outliers
- 🧰 Built with Pandas & NumPy

## What is Z-Test Outlier Detection?

Z-Test identifies outliers by measuring how far a data point is from the mean:
```𝑍 = (𝑥 − 𝜇) / σ```

A data point is an outlier if: ```|𝑍| > threshold```
