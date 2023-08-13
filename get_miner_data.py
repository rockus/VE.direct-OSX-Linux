from execute_ssh_command import restart
import subprocess
import json
import paramiko
import time


def get_json_output(ip_address, port, command):
    try:
        full_command = f'echo \'{json.dumps(command)}\' | nc {ip_address} {port} | jq .'
        output = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT, text=True)
        parsed_output = json.loads(output)
        return parsed_output
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None

    
def is_miner_fully_booted(ip_address, port):
    max_attempts = 10
    current_attempt = 0
    
    while current_attempt < max_attempts:
        json_output = get_json_output(ip_address, port, command={"command": "summary"})
        
        if json_output and "STATUS" in json_output and "SUMMARY" in json_output:
            status = json_output["STATUS"][0]["STATUS"]
            summary = json_output["SUMMARY"][0]["SUMMARY"]
            
            # Check if the status and summary indicate that the miner is fully booted
            if status == "S" and summary == "Booted":
                return True
        
        # Wait for a few seconds before the next attempt
        if current_attempt == 0:
            print("waiting for miner to boot")
        else:
            print("still waiting for miner to boot, attempt: ", current_attempt)
        time.sleep(5)
        current_attempt += 1
    
    # If max_attempts are reached and the miner is not fully booted, return False
    return False


def get_miner_power(ip_address, port, depth = 0):
    json_output = get_json_output(ip_address, port, command={"command": "tunerstatus"})
    if json_output:
        try:
            approximate_power_consumption = json_output['TUNERSTATUS'][0]['ApproximateChainPowerConsumption']
            approximate_miner_power_consumption = json_output['TUNERSTATUS'][0]['ApproximateMinerPowerConsumption']
            power = {
                "chain power": approximate_power_consumption,
                "miner power": approximate_miner_power_consumption
            }
            return power
        except KeyError as e:
            print("KeyError:", e)
            print("JSON Output:", json_output)  # Print the content of the JSON output for debugging

            # Read SSH credentials from ssh_config.json
            with open('ssh_config.json') as config_file:
                ssh_config = json.load(config_file)
                miner_ip_address = ssh_config['miner_ip_address']
                ssh_username = ssh_config['ssh_username']
                ssh_password = ssh_config['ssh_password']

            restart(miner_ip_address, ssh_username, ssh_password)

            if depth > 0:
                return None
            
            if is_miner_fully_booted(ip_address, port):
                return get_miner_power(ip_address, port, depth = depth + 1)
            
