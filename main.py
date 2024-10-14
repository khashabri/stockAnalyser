import yfinance as yf
import numpy as np
from tabulate import tabulate
import os
import sys
from progress.bar import IncrementalBar
import psutil
from symbols_dataset import *
import time

########################### Paramters ###########################

start_date = "2023-01-01";
end_date = None; # None or e.g. "2020-12-06"

# List of company tickers
companies = [
    "AAPL", "AXP", "BA", "CAT", "CSCO", "CVX", "DIS", "DOW", "GS", "HD", "IBM", "INTC",
    "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PFE", "PG", "TRV", "UNH",
    "RTX", "V", "VZ", "WBA", "WMT", "XOM", "AMZN", "GOOGL", "META", "BRK.AX", "NVDA"
] # or e.g. companies = us_market

############################ Helpers #############################
class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def start(self):
        self.tstart = time.time()

    def stop(self):
        if self.name:
            print('[%s]' % self.name,)
        # print('Elapsed: %s' % (time.time() - self.tstart))
        return time.time() - self.tstart


def printTime(remainedTime):
    print('\x1b[6;30;43m' + "Remained time: {:.4f}[min] or {:.0f}[s]"
            .format(remainedTime / 60, remainedTime) + '\x1b[0m')

# Remove duplicate companies
companies = list(dict.fromkeys(companies))

# Define table headers for displaying data
headers = [
    "Rank", "ID", "Company", "Evaluation Point", "Ratio Pos. Days", "Netto Growth", 
    "Mean Rel. Daily Growth", "Tot. Growth", "Current Price", "Sector"
]

# Function to evaluate the company based on given metrics
def evaluate(rel_num_of_pos, mean_rel_growth, total_rel_growth):
    return ((1/3) * rel_num_of_pos + (1/3) * mean_rel_growth + (1/3) * total_rel_growth) * 10

# Function to print the list of companies with their evaluated metrics
def print_the_list(this_list):
    os.system('clear')  # Clear the terminal screen
    mytable = []
    rank = 1
    for i in range(len(this_list)):
        # Append each company's data in a formatted row
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

    # table_str = tabulate(mytable, headers, tablefmt="grid")  # Get the table as a string
 
    # Construct the markdown table header
    table_str = "| " + " | ".join(headers) + " |\n"
    table_str += "| " + " | ".join(['---' for _ in headers]) + " |\n"

    # Add rows to the markdown table
    for row in mytable:
        table_str += "| " + " | ".join(row) + " |\n"

    table_str += f"\n{start_date} - {end_date}"  # Add the date range to the output

    # Save in the same directory
    output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.md")

    with open(output_file_path, "w") as file:
        file.write(table_str)

    print(table_str)

# Initialize necessary lists and variables
list_of_all_catched_data = []
error_list = []
myTimer = Timer()
nmb_of_comp = len(companies)
remained_nmb_of_comp = nmb_of_comp

os.system('clear')  # Clear the terminal screen
IncrementalBar = IncrementalBar('Processing', max=nmb_of_comp)  # Initialize a progress bar

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
        
        # Process the downloaded data
        x = data["Adj Close"]
        x = x[np.logical_not(np.isnan(x))]
        x = np.array(x)

        # Calculate some metrics
        diffs = np.concatenate(([0], np.diff(x)))           # daily price difference 
        num_of_pos = np.count_nonzero(diffs > 0)            # number of bullish days
        nettoGrowth = x[-1] - x[0]
        rel_num_of_pos = num_of_pos / len(diffs)            # relative number of bullish days to total number of days
        mean_rel_growth = np.mean(diffs[1:] / x[:-1])       # difference of closed price btw two days devided by closed of first day
        total_rel_growth = nettoGrowth / x[0]               # total relative change

        evaluation = evaluate(rel_num_of_pos, mean_rel_growth, total_rel_growth)
        
        # Get currency and current price
        try:
            comp = yf.Ticker(company)
            current_price = comp.info.get("ask", 0)
            currency = comp.info.get("currency", "")
            name = comp.info.get("shortName", "")
            sector = comp.info.get("sector", "")
        except:
            # Fallback if comp.info doesn't work
            data = yf.download(tickers=company)
            x_current = data["Open"]
            current_price = x_current[-1] if not x_current.empty else 0
            currency, name, sector = "", "", ""

        sys.stdout = sys.__stdout__  # Restore stdout

        catched_data = [evaluation, rel_num_of_pos, nettoGrowth, mean_rel_growth, total_rel_growth, current_price]

        # Remove None from eval metrics and comp infos
        catched_data = [0 if v is None else v for v in catched_data]
        catched_data = [company, np.array(catched_data), currency, name, sector]
        catched_data = [0 if v is None else v for v in catched_data]
        
        list_of_all_catched_data.append(catched_data)
        
        # Update the loading bar
        os.system('clear')
        IncrementalBar.next()
        print("\n CPU usage: {:}%".format(psutil.cpu_percent()))
        remained_nmb_of_comp -= 1
        printTime(remained_nmb_of_comp * myTimer.stop())
    
    except Exception as e:
        error_list.append(company)  # Append to error list if there's an issue
        os.system('clear')
        IncrementalBar.next()

IncrementalBar.finish()

# Sort the list of companies by their evaluation value
list_of_all_catched_data.sort(key=lambda x: x[1][0], reverse=True)

# Print the sorted list
print_the_list(list_of_all_catched_data)

# Print the companies that had errors
if error_list:
    print("Error in:", error_list)
