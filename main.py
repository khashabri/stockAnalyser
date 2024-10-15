import yfinance as yf
import numpy as np
import os
import sys
from progress.bar import IncrementalBar
import psutil
import time
import datetime
from symbols_dataset import *

########################### Parameters ###########################
past_week = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
past_three_month = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
past_two_years = datetime.datetime(datetime.datetime.now().year - 1, 1, 1).strftime("%Y-%m-%d")

# Different date ranges and company lists with keys to iterate over
date_configs = [
    {"start_date": past_week, "end_date": None}, # one week ago (7 days) result
    {"start_date": past_three_month, "end_date": None}, # three months ago (90 days) result
    {"start_date": past_two_years, "end_date": None} # last year (1.x year) result
]

company_configs = [
    {"key": "Big Tech", "companies": [
    "AAPL", "AXP", "BA", "CAT", "CSCO", "CVX", "DIS", "DOW", "GS", "HD", "IBM", "INTC",
    "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PFE", "PG", "TRV", "UNH",
    "RTX", "V", "VZ", "WBA", "WMT", "XOM", "AMZN", "GOOGL", "META", "BRK.AX", "NVDA"
    ]},    
    {"key": "NASDAQ", "companies": us_market},
    {"key": "DAX", "companies": de_market}
]

company_configs = [
    {"key": "Big Tech", "companies": [
    "AAPL", "AXP", "BA", "CAT", "CSCO", "CVX", "DIS", "DOW", "GS", "HD", "IBM", "INTC",
    "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PFE", "PG", "TRV", "UNH",
    "RTX", "V", "VZ", "WBA", "WMT", "XOM", "AMZN", "GOOGL", "META", "BRK.AX", "NVDA"
    ]}
]

############################ Helpers #############################
class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def start(self):
        self.tstart = time.time()

    def stop(self):
        return time.time() - self.tstart

def printTime(remainedTime):
    print('\x1b[6;30;43m' + "Remained time: {:.4f}[min] or {:.0f}[s]"
            .format(remainedTime / 60, remainedTime) + '\x1b[0m')

# Function to evaluate the company based on given metrics
def evaluate(rel_num_of_pos, mean_rel_growth, total_rel_growth):
    return ((1/3) * rel_num_of_pos + (1/3) * mean_rel_growth + (1/3) * total_rel_growth) * 10

# Function to print and return the markdown table for a specific company list
def print_the_list(this_list, start_date, end_date, key):
    headers = ["Rank", "ID", "Company", "Evaluation Point", "Ratio Pos. Days", "Netto Growth", 
    "Mean Rel. Daily Growth", "Tot. Growth", "Current Price", "Sector"]

    mytable = []
    rank = 1
    for i in range(len(this_list)):
        mytable.append([
            "{:}".format(rank), 
            this_list[i][0], 
            this_list[i][3], 
            "{:.2f}p".format(this_list[i][1][0]),
            "{:.4f}%".format(this_list[i][1][1] * 100),
            "{:.2f} ".format(this_list[i][1][2]) + this_list[i][2],
            "{:.2f}%".format(this_list[i][1][3] * 100),
            "{:.2f}%".format(this_list[i][1][4] * 100), 
            "{:.2f} ".format(this_list[i][1][5]) + this_list[i][2], 
            this_list[i][4]
        ])
        rank += 1
    
    if start_date == past_week:
        table_title = f"{key}_Last_Week"
    elif start_date == past_three_month:
        table_title = f"{key}_Last_Three_Months"
    elif start_date == past_two_years:
        table_title = f"{key}_Last_Year"
    else:
        table_title = f"{key}_From_{start_date}_until_{end_date if end_date else 'Today'}"

    table_str = f"## Results for {key} - {table_title.replace('_', ' ')}\n\n"
    table_str += f"| " + " | ".join(headers) + " |\n"
    table_str += "| " + " | ".join(['---' for _ in headers]) + " |\n"

    for row in mytable:
        table_str += "| " + " | ".join(row) + " |\n"

    return table_str, table_title

# Initialize necessary variables
error_list = []
myTimer = Timer()

# Path to the output directory
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Result")

# Create the output directory if it doesn't exist, or clear it if it does
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
else:
    # Clear existing files in the directory
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))

# Loop through each company and date configuration
for config in date_configs:
    start_date = config["start_date"]
    end_date = config["end_date"]

    for company_config in company_configs:
        key = company_config["key"]
        companies = company_config["companies"]

        list_of_all_catched_data = []
        companies = list(dict.fromkeys(companies))  # Remove duplicate companies
        nmb_of_comp = len(companies)
        remained_nmb_of_comp = nmb_of_comp

        os.system('clear')  # Clear the terminal screen
        incrementalBar = IncrementalBar('Processing', max=nmb_of_comp)  # Initialize a progress bar

        # Loop through each company to download and process its data
        for company in companies:
            myTimer.start()  # Start the timer for the company
            try:
                sys.stdout = open(os.devnull, "w")  # Suppress stdout
                data = yf.download(
                    tickers=company,
                    start=start_date,
                    end=end_date,
                    interval="1d",
                    group_by='ticker'
                )
                
                x = data["Adj Close"]
                x = x[np.logical_not(np.isnan(x))]
                x = np.array(x)
                if x[-1] < 2: continue # cheap penny stock founded

                diffs = np.concatenate(([0], np.diff(x)))           # daily price difference 
                num_of_pos = np.count_nonzero(diffs > 0)            # number of bullish days
                nettoGrowth = x[-1] - x[0]
                rel_num_of_pos = num_of_pos / len(diffs)            # relative number of bullish days to total number of days
                mean_rel_growth = np.mean(diffs[1:] / x[:-1])       # difference of closed price btw two days devided by closed of first day
                total_rel_growth = nettoGrowth / x[0]               # total relative change

                evaluation = evaluate(rel_num_of_pos, mean_rel_growth, total_rel_growth)
                
                try:
                    comp = yf.Ticker(company)
                    current_price = comp.info.get("ask", 0)
                    currency = comp.info.get("currency", "")
                    name = comp.info.get("shortName", "")
                    sector = comp.info.get("sector", "")
                except:
                    data = yf.download(tickers=company)
                    x_current = data["Open"]
                    current_price = x_current[-1] if not x_current.empty else 0
                    currency, name, sector = "", "", ""

                sys.stdout = sys.__stdout__  # Restore stdout

                catched_data = [evaluation, rel_num_of_pos, nettoGrowth, mean_rel_growth, total_rel_growth, current_price]
                catched_data = [0 if v is None else v for v in catched_data]
                catched_data = [company, np.array(catched_data), currency, name, sector]
                catched_data = [0 if v is None else v for v in catched_data]
                
                list_of_all_catched_data.append(catched_data)
                
                os.system('clear')
                incrementalBar.next()
                print("\n CPU usage: {:}%".format(psutil.cpu_percent()))
                remained_nmb_of_comp -= 1
                printTime(remained_nmb_of_comp * myTimer.stop())
            
            except Exception as e:
                error_list.append(company)
                os.system('clear')
                incrementalBar.next()

        incrementalBar.finish()

        # Sort the list of companies by their evaluation value
        list_of_all_catched_data.sort(key=lambda x: x[1][0], reverse=True)

        # Generate the markdown table and file name for the current config
        table_md, table_title = print_the_list(list_of_all_catched_data, start_date, end_date, key)

        # Define the path for the individual result file
        result_file_path = os.path.join(output_dir, f"{table_title}.md")

        # Write the result to the individual file
        with open(result_file_path, "w") as file:
            # Write the last run time at the start of the file
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"> Last update on: {current_time}\n\n")
            file.write(table_md + "\n\n")

# Print the companies that had errors
if error_list:
    print("Error in:", error_list)
