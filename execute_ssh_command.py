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

import paramiko
import json

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


def check_running(miner_ip_address, ssh_username, ssh_password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(miner_ip_address, username=ssh_username, password=ssh_password)
        ssh_command = "systemctl is-active bosminer"  # Check if the miner service is active
        stdin, stdout, stderr = ssh_client.exec_command(ssh_command)
        print("Running status: ", stdout.read().decode("utf-8").strip())
        return stdout.read().decode("utf-8").strip() == "active"
    except paramiko.AuthenticationException as auth_ex:
        print("Authentication error:", auth_ex)
        return False
    except paramiko.SSHException as ssh_ex:
        print("SSH connection error:", ssh_ex)
        return False
    finally:
        ssh_client.close()

def start_miner(miner_ip_address, ssh_username, ssh_password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(miner_ip_address, username=ssh_username, password=ssh_password)
        ssh_command = "systemctl start bosminer"  # Start the miner service
        stdin, stdout, stderr = ssh_client.exec_command(ssh_command)
        print_output(stdout.read().decode("utf-8"))
    except paramiko.AuthenticationException as auth_ex:
        print("Authentication error:", auth_ex)
    except paramiko.SSHException as ssh_ex:
        print("SSH connection error:", ssh_ex)
    finally:
        ssh_client.close()
