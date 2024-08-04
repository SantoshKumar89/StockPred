# main_script.py

import subprocess


def run_script_with_args(script_path, arg1, arg2):

    command = ["python3", script_path, arg1, arg2]
    print(f"Running command: {' '.join(command)}")  # Debugging line
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Script executed successfully:")
        print(result.stdout)
    else:
        print("Error executing script:")
        print(result.stderr)


def main():
    script_path = "playground_hourly_high_multi_input_forecast.py"
    stockname = "NIFTY 50"
    symbol = "^NSEI"
    start_date = "2022-08-25"
    start_time = "00:00:00"
    end_date = "2024-07-25"
    end_time = "10:15:00"
    interval = "1h"
    input_sequence_length = 35
    output_sequence_length = 1

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
