from get_pannel_data import check_voltage
from get_miner_data import check_running
from get_pannel_data import scan_charge_controller
import json


# Read SSH credentials from ssh_config.json
with open('ssh_config.json') as config_file:
    ssh_config = json.load(config_file)
    miner_ip_address = ssh_config['miner_ip_address']
    ssh_username = ssh_config['ssh_username']
    ssh_password = ssh_config['ssh_password']
    miner_port = ssh_config['miner_port']


def ensure_running(miner_ip_address):
    print("ping 1")
    if not check_running(miner_ip_address, miner_port):
        print("ping 2")
        start_miner(miner_ip_address)
        print("ping 3")

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


def ensure_running(miner_ip_address):
    if not check_running(miner_ip_address, miner_port):
        start_miner(miner_ip_address)

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


while True:
    charge_controller = scan_charge_controller()
    print("\nBattery voltage: ", check_voltage(charge_controller))
    print("Miner running status: ", check_running(miner_ip_address, miner_port))
    print(charge_controller)
    print("\n")
