# main_script.py

import subprocess


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
        "python3",
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
    retry = 0

    while(retry < 5): 
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("Script executed successfully:")
            if 'Not Working' in result.stdout:
                retry = retry + 1
                print(f'Not Working, Trying again!! retry={retry} ')
            else:
                print('Working')          
                print('Result saved!!')
                break
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
    input_sequence_length = "35"
    output_sequence_length = "1"

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
