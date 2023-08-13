from get_miner_data import get_miner_power
from get_pannel_data import scan_charge_controller
from execute_ssh_command import execute_ssh_command
from execute_ssh_command import load_ssh_config


# Example usage:
miner_ip_address = '192.168.8.194'
miner_port = '4028'

miner_power = get_miner_power(miner_ip_address, miner_port)
pannel_data = scan_charge_controller()

print("Miner Data:", miner_power)
print("Pannel Data:", pannel_data)


def set_power_target(power_target = 100):

    # Load SSH configuration from the JSON file
    ssh_config = load_ssh_config()

    # Example usage:
    miner_ip_address = ssh_config["miner_ip_address"]
    ssh_username = ssh_config["ssh_username"]
    ssh_password = ssh_config["ssh_password"]


    # SSH command
    ssh_command = f"sed -i 's/^power_target = .*/power_target = {power_target}/' /etc/bosminer.toml && /etc/init.d/bosminer restart"

    # Execute the SSH command
    command_output = execute_ssh_command(miner_ip_address, ssh_username, ssh_password, ssh_command)


    # Print the command output if it's non-empty
    if command_output.strip():
        print("Command Output:")
        print(command_output)

set_power_target(50)
