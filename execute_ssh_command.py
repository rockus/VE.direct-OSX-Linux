import paramiko
import json

def load_ssh_config():
    with open("ssh_config.json", "r") as config_file:
        return json.load(config_file)

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

