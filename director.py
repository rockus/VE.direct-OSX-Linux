from get_miner_data import get_miner_power
from get_pannel_data import scan_charge_controller
from execute_ssh_command import execute_ssh_command
from execute_ssh_command import restart
from execute_ssh_command import load_ssh_config
from execute_ssh_command import stop_miner
from execute_ssh_command import start_miner
from execute_ssh_command import check_running
from execute_ssh_command import print_output
import time
import json
import os


# Check if the lock file exists
lock_file_path = "/tmp/director.lock"
if os.path.exists(lock_file_path):
    print("Script is already running. Exiting.")
    exit(0)

# Create the lock file
with open(lock_file_path, "w") as lock_file:
    lock_file.write(str(os.getpid()))


# Read SSH credentials from ssh_config.json
with open('ssh_config.json') as config_file:
    ssh_config = json.load(config_file)
    miner_ip_address = ssh_config['miner_ip_address']
    ssh_username = ssh_config['ssh_username']
    ssh_password = ssh_config['ssh_password']
    miner_port = ssh_config['miner_port']


def ensure_running(miner_ip_address, ssh_username, ssh_password):
    if not check_running(miner_ip_address, ssh_username, ssh_password):
        start_miner(miner_ip_address, ssh_username, ssh_password)

def set_power_target(miner_ip_address, ssh_username, ssh_password, power_target = 152):

    minimum_power, maximum_power = 100, 600

    if power_target > maximum_power:
        power_target = maximum_power

    if power_target < minimum_power:
        stop_miner(miner_ip_address, ssh_username, ssh_password)

    if power_target >= minimum_power and power_target <= maximum_power:
        ensure_running(miner_ip_address, ssh_username, ssh_password)


    # SSH command
    # ssh_command = f"sed -i 's/^power_target = .*/power_target = {power_target}/' /etc/bosminer.toml && /etc/init.d/bosminer restart"
    ssh_command = f"sed -i 's/^power_target = .*/power_target = {power_target}/' /etc/bosminer.toml"

    # Execute the SSH command
    print_output(execute_ssh_command(miner_ip_address, ssh_username, ssh_password, ssh_command))
    print_output(restart(miner_ip_address, ssh_username, ssh_password))


# set_power_target(152)
def determine_delta():

    panel_data = scan_charge_controller()
    if check_running(miner_ip_address, ssh_username, ssh_password):
        miner_power = get_miner_power(miner_ip_address, miner_port)

        print("Miner Data:", miner_power)
        print("Pannel Data:", panel_data)

        return panel_data["panel_power"] - miner_power["miner power"]
    else:
        print("Pannel Data:", panel_data)
        return panel_data["panel_power"]


def check_voltage():
    panel_data = scan_charge_controller()
    battery_voltage_str = panel_data["battery_voltage"]
    try:
        battery_voltage = float(battery_voltage_str)
        return battery_voltage
    except ValueError:
        print("Error converting battery voltage to numeric value:", battery_voltage_str)
        return 0.0  # Return a default value (you can adjust this as needed)

def show_progress_bar(wait_time_seconds):
    # Initialize the progress bar variables
    progress = 0
    progress_bar_length = 30

    print("Let's give the miner some time to stabilize its fan speed before we change things again:")
    sys.stdout.write("[{}]".format(" " * progress_bar_length))
    sys.stdout.flush()

    # Split the wait time into smaller intervals for updating the progress bar
    interval = wait_time_seconds / progress_bar_length

    # Loop through the intervals and update the progress bar
    for _ in range(progress_bar_length):
        time.sleep(interval)
        progress += 1
        sys.stdout.write("\r[{}{}]".format("=" * progress, " " * (progress_bar_length - progress)))
        sys.stdout.flush()

    print("\nStabilization time complete.")


def on():
    # set_power_target(miner_ip_address, ssh_username, ssh_password, 100)
    # Set it to true for this to work
    if check_voltage() > 13:
        isrunning = check_running(miner_ip_address, ssh_username, ssh_password)
        if isrunning:
            miner_power = get_miner_power(miner_ip_address, miner_port)["panel_power"]
            small_delta = (determine_delta() / miner_power) < 0.15
        else:
            small_delta = (determine_delta() / 152) < 0.15

        if determine_delta() > 0 and small_delta:
            # Ignore increases if they are insignificant, because the miner wastes energy when restarting
            print("Not increasing the miners settings because delta is small")
        else:
            if check_running(miner_ip_address, ssh_username, ssh_password):
                new_power = get_miner_power(miner_ip_address, miner_port)["miner power"] + determine_delta()
            else:
                new_power = determine_delta()
                
            ensure_running(miner_ip_address, ssh_username, ssh_password)
            while not check_running(miner_ip_address, ssh_username, ssh_password):
                print("Waiting for the miner to start")
                time.sleep(5)
            print("Changing miner power to ", new_power)
            set_power_target(miner_ip_address, ssh_username, ssh_password, new_power)

            # wait_time_seconds = 10 * 60  # Convert 10 minutes to seconds
            print("Lets give the miner some time to stabilize its can speed before we chage things again")
            wait_time_seconds = 60 * 3
            show_progress_bar(wait_time_seconds)


def off():
    first = True

    if check_voltage() < 12:
        if check_running(miner_ip_address, ssh_username, ssh_password) and first:
            print("Voltage < 12 V. Turning off the miner")
            stop_miner(miner_ip_address, ssh_username, ssh_password)

        if check_running(miner_ip_address, ssh_username, ssh_password) and first:
            print("The miner is on again even thought eh voltage is still < 12 V!")
            print("Turning off the miner")
            stop_miner(miner_ip_address, ssh_username, ssh_password)

            
def run_minimal():
    # set_power_target(miner_ip_address, ssh_username, ssh_password, 100)
    # Set it to true for this to work

    if 12 < check_voltage() and check_voltage() < 13:
        if check_running(miner_ip_address, ssh_username, ssh_password):
            miner_stats = get_miner_power(miner_ip_address, miner_port)
            if miner_stats != None:
                miner_power_consumption = miner_stats["miner power"]

                if miner_power_consumption > 160:
                    set_power_target(miner_ip_address, ssh_username, ssh_password, 100)
            else:
                raise Exception("Weird: The miner is running, but no stats...")
        else:
            print("The miner is already off, lets wait for 13 Volt before starting")
        
        # wait_time_seconds = 10 * 60  # Convert 10 minutes to seconds
        # wait_time_seconds = 60
        # time.sleep(wait_time_seconds)

print("Battery voltage: ", check_voltage())
print("Miner running status: ", check_running(miner_ip_address, ssh_username, ssh_password))
print(scan_charge_controller())
run_minimal()
on()
off()


# Remove the lock file when the script is done
os.remove(lock_file_path)

