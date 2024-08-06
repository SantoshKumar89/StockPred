# main_script.py

import subprocess
import yfinance as yf
import time
import sys

def run_script_with_args(
    script_path,
    stockname,
    symbol,
    start_date,
    start_time,
    end_date,
    end_time,
    interval,
    input_sequence_length,
    output_sequence_length,
    output_csv_path,
):
    
    command = [
        "/usr/local/bin/python3",
        script_path,
        stockname,
        symbol,
        start_date,
        start_time,
        end_date,
        end_time,
        interval,
        input_sequence_length,
        output_sequence_length,
        output_csv_path,
    ]
    #print(f"Running command: {' '.join(command)}")  # Debugging line
    retry = 0

    while retry < 5:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("Script executed successfully:")
            if "Not-Working" in result.stdout:
                retry = retry + 1
                print(f"Not Working, Trying again!! retry={retry} ")
                #print(result.stdout)
            else:
                print("Working")
                print("Result saved!!")
                #print(result.stdout)
                break
        else:
            print(result.stderr)
            sys.exit("Stopping execution due to failure.")


def main():
    script_path = "playground_hourly_high_multi_input_forecast.py"
    output_csv_path = "output.csv"
    stockname = "NIFTY50"
    symbol = "^NSEI"
    input_sequence_length = "35"
    output_sequence_length = "1"
    interval = "1h"

    df = yf.download(symbol, end="2024-07-30", start="2024-07-01", interval=interval)
    start_date = "2022-08-25"
    start_time = "00:00:00"

    # Loop Through the Yahoo Finance Data
    for index, row in df.iterrows():
        end_date = str(index.date())
        end_time = str(index.time())

        print(f"Prediction for {end_date} {end_time} Started")
        execition_start_time = time.time()
        run_script_with_args(
            script_path,
            stockname,
            symbol,
            start_date,
            start_time,
            end_date,
            end_time,
            interval,
            input_sequence_length,
            output_sequence_length,
            output_csv_path
        )
        execition_end_time = time.time()
        print(f"Prediction for {end_date} {end_time} Completed")
        print(f"Execution time: {execition_end_time - execition_start_time } seconds")


if __name__ == "__main__":
    main()
