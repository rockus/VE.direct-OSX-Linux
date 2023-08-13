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
    miner_power = get_miner_power(miner_ip_address, miner_port)
    panel_data = scan_charge_controller()

    print("Miner Data:", miner_power)
    print("Pannel Data:", panel_data)

    return panel_data["panel_power"] - miner_power["miner power"]


while True:
    if determine_delta() > 0 and (determine_delta() / get_miner_power(miner_ip_address, miner_port)["panel_power"]) < 0.15:
        # Ignore increases if they are insignificant, because the miner wastes energy when restarting
        pass
    else:
        set_power_target(miner_ip_address, ssh_username, ssh_password, get_miner_power(miner_ip_address, miner_port)["miner power"] + determine_delta())
    wait_time_seconds = 10 * 60  # Convert 10 minutes to seconds
    time.sleep(wait_time_seconds)
