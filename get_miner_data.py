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

# Example usage:
ip_address = '192.168.8.194'
port = '4028'


def get_miner_power():
    json_output = get_json_output(ip_address, port, command={"command": "tunerstatus"})
    if json_output:
        # print(json.dumps(json_output, indent=2))
        approximate_power_consumption = json_output['TUNERSTATUS'][0]['ApproximateChainPowerConsumption']
        approximate_miner_power_consumption = json_output['TUNERSTATUS'][0]['ApproximateMinerPowerConsumption']

        """
        print("Approximate Chain Power Consumption:", approximate_power_consumption)
        print("Approximate Miner Power Consumption:", approximate_miner_power_consumption)
        """


        power = {
            "chain power": approximate_power_consumption,
            "miner power": approximate_miner_power_consumption
        }

        return power

