## Stock Analysis and Evaluation Tool

This repository contains a Python script designed to evaluate and rank a list of companies based on their stock performance. It utilizes various metrics to assess each company's stock growth and performance over a specified period.

### Key Features

- **Data Retrieval**: Uses `yfinance` to download historical stock data for a list of companies.
- **Data Processing**: Calculates key metrics such as the number of positive days, net growth, mean relative daily growth, and total relative growth.
- **Evaluation**: Computes an overall evaluation score for each company based on the calculated metrics.
- **Output**: Displays and saves a formatted table of evaluated companies, ranked by their performance.

### Key Performance Metrics
1. **Ratio of Positive Days (rel_num_of_pos)**
   - **Definition**: The ratio of days the stock price increased compared to the total number of days.
   - **Calculation**: 
     ```python
     rel_num_of_pos = num_of_pos / len(diffs)
     ```
   - **Interpretation**: A higher ratio indicates a more consistently bullish stock.

2. **Mean Relative Daily Growth (mean_rel_growth)**
   - **Definition**: The average daily percentage change in the stock price.
   - **Calculation**:
     ```python
     mean_rel_growth = np.mean(diffs[1:] / x[:-1])
     ```
   - **Interpretation**: A higher mean relative growth indicates more significant average daily gains.

3. **Total Growth (total_rel_growth)**
   - **Definition**: The overall percentage change in stock price over the entire period.
   - **Calculation**:
     ```python
     total_rel_growth = nettoGrowth / x[0]
     ```
   - **Interpretation**: A higher total growth indicates a more significant overall increase in stock value.

4. **Evaluation Score**
   - **Definition**: A composite score evaluating the overall performance of the stock.
   - **Calculation**:
     ```python
     evaluation = ((1/3) * rel_num_of_pos + (1/3) * mean_rel_growth + (1/3) * total_rel_growth) * 10
     ```
   - **Interpretation**: Combines the above metrics to provide a balanced evaluation score. A higher score indicates better performance.

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
