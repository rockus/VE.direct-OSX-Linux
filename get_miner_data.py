import requests
import paramiko
import json
import subprocess
import time
#from get_miner_data import get_miner_power


def get_json_output(ip_address, port, command):
    try:
        full_command = f'echo \'{json.dumps(command)}\' | nc {ip_address} {port} | jq .'
        output = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT, text=True)

        try:
            parsed_output = json.loads(output)
            return parsed_output
        except json.JSONDecodeError as json_error:
            print("Error parsing JSON:", json_error)
            return None

    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None

 #from get_miner_data import get_miner_power
#from get_pannel_data import 
import subprocess

"""
def check_paramiko_installed():
    try:
        subprocess.run(["pip3", "show", "paramiko"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def install_paramiko():
    if not check_paramiko_installed():
        try:
            subprocess.run(["pip3", "install", "paramiko"], check=True)
            print("paramiko installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error installing paramiko:", e)
    else:
        print("paramiko is already installed.")

# Call the function to install paramiko if needed
install_paramiko()
"""

def load_ssh_config():
    with open("ssh_config.json", "r") as config_file:
        return json.load(config_file)

def print_output(command_output):
    if command_output != None:
        if command_output.strip():
            print("Command Output:")
            print(command_output)

def execute_ssh_command(ip_address, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(ip_address, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return stdout.read().decode()
    except paramiko.AuthenticationException:
        return "Authentication failed."
    except paramiko.SSHException as e:
        return f"SSH error: {str(e)}"
    finally:
        ssh_client.close()



def stop_miner(ip_address, ssh_username, ssh_password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(ip_address, username=ssh_username, password=ssh_password)
        ssh_command = "systemctl stop bosminer"  # Stop the miner service
        stdin, stdout, stderr = ssh_client.exec_command(ssh_command)
        print_output(stdout.read().decode("utf-8"))
    except paramiko.AuthenticationException as auth_ex:
        print("Authentication error:", auth_ex)
    except paramiko.SSHException as ssh_ex:
        print("SSH connection error:", ssh_ex)
    finally:
        ssh_client.close()


def running_attempt(ip_address, port):
    command = {"command": "summary"}  # Use the appropriate JSON command to check miner status
    output = get_json_output(ip_address, port, command)

    # print("Attempt", current_attempt + 1)
    if output:
        status_list = output.get("STATUS", [])
        for status_entry in status_list:
            if "STATUS" in status_entry and status_entry["STATUS"] == "S":
                return True  # Miner is running


def check_running(ip_address, port):
    max_attempts = 10
    current_attempt = 0
    sleep_duration = 5  # in seconds

    running_attempt(ip_address, port)
    """
    while current_attempt < max_attempts:
        running_attempt()

        current_attempt += 1
        if current_attempt < max_attempts:
            # print("Retrying in", sleep_duration, "seconds...")
            time.sleep(sleep_duration)
    """

    # If no valid output is obtained after max_attempts, raise an exception
    # raise Exception("Miner is not running after multiple attempts")
    return False
 


"""
def check_paramiko_installed():
    try:
        subprocess.run(["pip3", "show", "paramiko"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def install_paramiko():
    if not check_paramiko_installed():
        try:
            subprocess.run(["pip3", "install", "paramiko"], check=True)
            print("paramiko installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error installing paramiko:", e)
    else:
        print("paramiko is already installed.")

# Call the function to install paramiko if needed
install_paramiko()
"""

def load_ssh_config():
    with open("ssh_config.json", "r") as config_file:
        return json.load(config_file)

def print_output(command_output):
    if command_output != None:
        if command_output.strip():
            print("Command Output:")
            print(command_output)

def execute_ssh_command(ip_address, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(ip_address, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return stdout.read().decode()
    except paramiko.AuthenticationException:
        return "Authentication failed."
    except paramiko.SSHException as e:
        return f"SSH error: {str(e)}"
    finally:
        ssh_client.close()




def stop_miner(ip_address, ssh_username, ssh_password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(ip_address, username=ssh_username, password=ssh_password)
        ssh_command = "systemctl stop bosminer"  # Stop the miner service
        stdin, stdout, stderr = ssh_client.exec_command(ssh_command)
        print_output(stdout.read().decode("utf-8"))
    except paramiko.AuthenticationException as auth_ex:
        print("Authentication error:", auth_ex)
    except paramiko.SSHException as ssh_ex:
        print("SSH connection error:", ssh_ex)
    finally:
        ssh_client.close()

# curl 'http://151.216.205.165/graphql' -X POST -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0' -H 'Accept: */*' -H 'Accept-Language: en' -H 'Accept-Encoding: gzip, deflate' -H 'content-type: application/json' -H 'Origin: http://151.216.205.165' -H 'Connection: keep-alive' -H 'Referer: http://151.216.205.165/' -H 'Cookie: session_id=ab29f38a41d1c6649ef004cfb935596d' --data-raw '{"query":"mutation {\n  bosminer {\n    start {\n      ... on BosminerError {\n        message\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n","variables":{}}'
# {"data":{"bosminer":{"__typename":"BosminerMutation","start":{"__typename":"VoidResult"}}}}


def start_miner(miner_ip_address):
    curl_command = (
        f"curl 'http://{miner_ip_address}/graphql' -X POST "
        "-H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0' "
        "-H 'Accept: */*' -H 'Accept-Language: en' -H 'Accept-Encoding: gzip, deflate' "
        "-H 'content-type: application/json' "
        f"-H 'Origin: http://{miner_ip_address}' "
        "-H 'Connection: keep-alive' "
        f"-H 'Referer: http://{miner_ip_address}/' "
        "-H 'Cookie: session_id=ab29f38a41d1c6649ef004cfb935596d' "
        "--data-raw '{\"query\":\"mutation {\\n  bosminer {\\n    start {\\n      ... on BosminerError {\\n        message\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{}}'"
    )

    try:
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        print("Curl Output:", result.stdout)
    except Exception as e:
        print("Error:", e)

   
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


def get_miner_power(ip_address, port, depth=0):
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
            # print("KeyError:", e)
            # print("JSON Output:", json_output)  # Print the content of the JSON output for debuggingf

            # Read SSH credentials from ssh_config.json
            with open('ssh_config.json') as config_file:
                ssh_config = json.load(config_file)
                ip_address = ssh_config['miner_ip_address']
                ssh_username = ssh_config['ssh_username']
                ssh_password = ssh_config['ssh_password']

            if check_running(ip_address, port):
                print("The miner is running, and we still got this error. Weird...")
            else:
                print("The miner is not running")
                
            """

            restart(ip_address, ssh_username, ssh_password)

            if depth > 0:
                return None
            
            if is_miner_fully_booted(ip_address, port):
                return get_miner_power(ip_address, port, depth = depth + 1)
            
            # Your error handling logic here
            # For example, you can return None or raise a custom exception
            """
            return None  # Returning None to indicate failure


"""
def check_paramiko_installed():
    try:
        subprocess.run(["pip3", "show", "paramiko"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def install_paramiko():
    if not check_paramiko_installed():
        try:
            subprocess.run(["pip3", "install", "paramiko"], check=True)
            print("paramiko installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error installing paramiko:", e)
    else:
        print("paramiko is already installed.")

# Call the function to install paramiko if needed
install_paramiko()
"""


def load_ssh_config():
    with open("ssh_config.json", "r") as config_file:
        return json.load(config_file)

def print_output(command_output):
    if command_output != None:
        if command_output.strip():
            print("Command Output:")
            print(command_output)

def execute_ssh_command(ip_address, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(ip_address, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return stdout.read().decode()
    except paramiko.AuthenticationException:
        return "Authentication failed."
    except paramiko.SSHException as e:
        return f"SSH error: {str(e)}"
    finally:
        ssh_client.close()


def restart(ip_address, ssh_username, ssh_password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip_address, username=ssh_username, password=ssh_password)

        # Execute the reboot command
        stdin, stdout, stderr = client.exec_command('reboot')
        print("Miner restarted successfully.")

        # Close the SSH connection
        client.close()
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication failed. Check the username and password.")
    except paramiko.ssh_exception.SSHException as e:
        print("SSH error:", e)
    except Exception as e:
        print("Error restarting miner:", e)


def stop_miner(miner_ip_address):
    curl_command = (
        f"curl 'http://{miner_ip_address}/graphql' -X POST "
        "-H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0' "
        "-H 'Accept: */*' -H 'Accept-Language: en' -H 'Accept-Encoding: gzip, deflate' "
        "-H 'content-type: application/json' "
        f"-H 'Origin: http://{miner_ip_address}' "
        "-H 'Connection: keep-alive' "
        f"-H 'Referer: http://{miner_ip_address}/' "
        "-H 'Cookie: session_id=ab29f38a41d1c6649ef004cfb935596d' "
        "--data-raw '{\"query\":\"mutation {\\n  bosminer {\\n    stop {\\n      ... on VoidResult {\\n        void\\n        __typename\\n      }\\n      ... on BosminerError {\\n        message\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{}}'"
    )

    try:
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        print("Curl Output:", result.stdout)
    except Exception as e:
        print("Error:", e)

