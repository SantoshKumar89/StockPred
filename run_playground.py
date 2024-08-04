# main_script.py

import subprocess
import yfinance as yf


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
    ]
    print(f"Running command: {' '.join(command)}")  # Debugging line
    retry = 0

    while retry < 5:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("Script executed successfully:")
            if "Not Working" in result.stdout:
                retry = retry + 1
                print(f"Not Working, Trying again!! retry={retry} ")
                print(result.stdout)
            else:
                print("Working")
                print("Result saved!!")
                print(result.stdout)
                break
        else:
            print("Error executing script:")
            print(result.stdout)


def main():
    script_path = "playground_hourly_high_multi_input_forecast.py"
    stockname = "NIFTY50"
    symbol = "^NSEI"
    input_sequence_length = "35"
    output_sequence_length = "1"
    interval = "1h"

    df = yf.download(symbol, end="2024-07-02", start="2024-07-01", interval=interval)
    start_date = "2022-08-25"
    start_time = "00:00:00"

    # Loop Through the Yahoo Finance Data
    for index, row in df.iterrows():
        print(index.date())
        end_date = str(index.date())
        end_time = str(index.time())
        #print(
        #    "Executing ===>",
        #    stockname,
        #    symbol,
        #    start_date,
        #    start_time,
        #    end_date,
        #    end_time,
        #    interval,
        #    input_sequence_length,
        #    output_sequence_length,
        #)
        #['/Users/santoshkumar/Documents/Repository/Stock_prediction_python/playground_hourly_high_multi_input_forecast.py', 'NIFTY 50', '^NSEI', '2022-08-25', '00:00:00', '2024-07-01', '09:15:00', '1h', '35', '1']

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
        )


if __name__ == "__main__":
    main()
