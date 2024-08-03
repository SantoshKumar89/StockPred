# main_script.py

import subprocess

def run_script_with_args(script_path, arg1, arg2):
    command = ['python3', script_path, arg1, arg2]
    print(f"Running command: {' '.join(command)}")  # Debugging line
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Script executed successfully:")
        print(result.stdout)
    else:
        print("Error executing script:")
        print(result.stderr)

def main():
    script_path = 'playground_hourly_high_multi_input_forecast.py'
    dynamic_arg1 = 'Hello'
    dynamic_arg2 = 'World'

    run_script_with_args(script_path, dynamic_arg1, dynamic_arg2)

if __name__ == "__main__":
    main()
