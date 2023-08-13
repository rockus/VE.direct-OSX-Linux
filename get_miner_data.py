import subprocess
import json

def get_json_output(ip_address, port, command):
    try:
        full_command = f'echo \'{json.dumps(command)}\' | nc {ip_address} {port} | jq .'
        output = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT, text=True)
        parsed_output = json.loads(output)
        return parsed_output
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None

    
def restart(ip_address):
    try:
        subprocess.run(["ssh", f"root@{ip_address}", "reboot"], check=True)
        print("Miner restarted successfully.")
    except subprocess.CalledProcessError as e:
        print("Error restarting miner:", e)


def get_miner_power(ip_address, port):
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

            restart(ip_address)

            return None
