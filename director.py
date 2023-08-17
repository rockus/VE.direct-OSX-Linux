from get_miner_data import get_miner_power
from monitor_miner import ensure_running
from get_pannel_data import scan_charge_controller
from get_pannel_data import check_voltage
from get_miner_data import execute_ssh_command
from get_miner_data import restart
from get_miner_data import load_ssh_config
from get_miner_data import stop_miner
from get_miner_data import start_miner
from get_miner_data import check_running
from get_miner_data import print_output
from get_miner_data import get_json_output
import time
import json
import os


# Read SSH credentials from ssh_config.json
with open('ssh_config.json') as config_file:
    ssh_config = json.load(config_file)
    miner_ip_address = ssh_config['miner_ip_address']
    ssh_username = ssh_config['ssh_username']
    ssh_password = ssh_config['ssh_password']
    miner_port = ssh_config['miner_port']
    upper_limit = ssh_config['upper_limit']
    lower_limit = ssh_config['lower_limit']


def set_power_target(miner_ip_address, ssh_username, ssh_password, power_target = 152):

    minimum_power, maximum_power = 100, 600

    if power_target > maximum_power:
        power_target = maximum_power

    if power_target < minimum_power:
        stop_miner(miner_ip_address, ssh_username, ssh_password)

    if power_target >= minimum_power and power_target <= maximum_power:
        ensure_running(miner_ip_address)


    # SSH command
    # ssh_command = f"sed -i 's/^power_target = .*/power_target = {power_target}/' /etc/bosminer.toml && /etc/init.d/bosminer restart"
    ssh_command = f"sed -i 's/^power_target = .*/power_target = {power_target}/' /etc/bosminer.toml"

    # Execute the SSH command
    print_output(execute_ssh_command(miner_ip_address, ssh_username, ssh_password, ssh_command))
    print_output(restart(miner_ip_address, ssh_username, ssh_password))


# set_power_target(152)
def determine_delta(charge_controller):

    if check_running(miner_ip_address, miner_port):
        miner_power = get_miner_power(miner_ip_address, miner_port)

        print("Miner Data:", miner_power)
        print("Pannel Data:", charge_controller)

        return charge_controller["panel_power"] - miner_power["miner power"]
    else:
        print("Pannel Data:", charge_controller)
        return charge_controller["panel_power"]


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


def on(charge_controller):
    # set_power_target(miner_ip_address, ssh_username, ssh_password, 100)
    # Set it to true for this to work
    if check_voltage(charge_controller) > upper_limit:
        isrunning = check_running(miner_ip_address, miner_port)
        if isrunning:
            miner_power = get_miner_power(miner_ip_address, miner_port)["panel_power"]
            small_delta = (determine_delta(charge_controller) / miner_power) < 0.15
        else:
            small_delta = (determine_delta(charge_controller) / 152) < 0.15

        if determine_delta(charge_controller) > 0 and small_delta:
            # Ignore increases if they are insignificant, because the miner wastes energy when restarting
            print("Not increasing the miners settings because delta is small")
        else:
            if check_running(miner_ip_address, miner_port):
                new_power = get_miner_power(miner_ip_address, miner_port)["miner power"] + determine_delta(charge_controller)
            else:
                new_power = determine_delta(charge_controller)
                
            while not check_running(miner_ip_address, miner_port):
                ensure_running(miner_ip_address)
                print("Waiting for the miner to start")
                time.sleep(5)

            print("Changing miner power to ", new_power)
            set_power_target(miner_ip_address, ssh_username, ssh_password, new_power)

            # wait_time_seconds = 10 * 60  # Convert 10 minutes to seconds
            print("Lets give the miner some time to stabilize its can speed before we chage things again")
            wait_time_seconds = 60 * 3
            show_progress_bar(wait_time_seconds)


def off(charge_controller):
    if check_voltage(charge_controller) < lower_limit:
        if check_running(miner_ip_address, miner_port):
            print("Voltage < 12 V. Turning off the miner")
            stop_miner(miner_ip_address, ssh_username, ssh_password)

        if check_running(miner_ip_address, miner_port):
            print("The miner is on again even thought eh voltage is still < 12 V!")
            print("Turning off the miner")
            stop_miner(miner_ip_address, ssh_username, ssh_password)

            
def run_minimal(charge_controller):
    # set_power_target(miner_ip_address, ssh_username, ssh_password, 100)
    # Set it to true for this to work

    voltage = check_voltage(charge_controller)

    if lower_limit < voltage and voltage < upper_limit:
        if check_running(miner_ip_address, miner_port):
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


# Check if the lock file exists                                           
lock_file_path = "/tmp/director.lock"
if os.path.exists(lock_file_path):
    print("Script is already running. Exiting.")
    exit(0)


# Create the lock file                                                    
with open(lock_file_path, "w") as lock_file:
    lock_file.write(str(os.getpid()))


def director_loop():
    charge_controller = scan_charge_controller()
    print("Battery voltage: ", check_voltage(charge_controller))
    print("Miner running status: ", check_running(miner_ip_address, miner_port))
    print(charge_controller)

    print("\n")
    # print("\nstart run_minimal")
    run_minimal(charge_controller)
    # print("\nstart on")
    on(charge_controller)
    # print("\nstart off")
    off(charge_controller)


while True:
    director_loop()

# Remove the lock file when the script is done
os.remove(lock_file_path)
