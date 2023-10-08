# Log File Analysis and Data Preparation

This Python script is designed to process log files related to a financial time series data analysis project. It performs data filtering, feature engineering, and data extraction tasks. The script prepares the data for further analysis, such as machine learning model training.

## Prerequisites

- Python
- MetaTrader5 (mt5)
- pandas
- pytz

## Usage

1. Clone this repository.
2. Modify the script's variables at the beginning of the file to specify your file paths and settings.
   - `folder_path`: Path to the folder containing log files.
   - `output_file`: Name of the Excel file to save the processed data.
   - `symbol`: The financial symbol (e.g., "NQ100_m") for which you want to analyze data.
   - Adjust other variables as needed for data filtering and feature engineering.
3. Run the script.

## Description

This script does the following:
- Loads log files related to financial time series data.
- Filters data based on volume, date, and time conditions.
- Performs data sorting, time zone conversion, and data annotation.
- Extracts historical price data (previous and future candles) for feature engineering.

The script is designed to prepare the data for further analysis, such as building machine learning models for financial prediction or analysis.

## License

This project is licensed under the [MIT License](LICENSE).
