## Stock Analysis and Evaluation Tool

This repository contains a Python script designed to evaluate and rank a list of companies based on their stock performance. It utilizes various metrics to assess each company's stock growth and performance over a specified period.

### Key Features

- **Data Retrieval**: Uses `yfinance` to download historical stock data for a list of companies.
- **Data Processing**: Calculates key metrics such as the number of positive days, net growth, mean relative daily growth, and total relative growth.
- **Evaluation**: Computes an overall evaluation score for each company based on the calculated metrics.
- **Output**: Displays and saves a formatted table of evaluated companies, ranked by their performance.

### Dependencies

- `yfinance`: For downloading historical stock data.
- `numpy`: For numerical operations and data processing.
- `tabulate`: For formatting the output table.
- `progress`: For displaying a progress bar during the data processing.
- `psutil`: For monitoring CPU usage.
- Custom modules:
  - `Timing`: Contains a timer utility.
  - `finanz_proj_database`: Assumed to be used for additional data handling or storage.

### Usage

**Setup**: Ensure all dependencies are installed. You can install the required packages using pip:
   ```sh
   pip install yfinance numpy tabulate progress psutil
   ```

**Run**: `python main.py`
