import subprocess
import json
import re

class NoUSBDeviceFoundError(Exception):
    pass


"""
def find_tty_usb_device_id_lsusb():
    try:
        # Use lsusb to list connected USB devices
        lsusb_output = subprocess.check_output(["lsusb"], stderr=subprocess.STDOUT, text=True)
        
        # Search for the USB device with FTDI ID
        pattern = r"ID\s+(\w+:\w+)\s+Future Technology Devices International"
        match = re.search(pattern, lsusb_output)
        if match:
            device_id = match.group(1)
            return device_id
        else:
            raise NoUSBDeviceFoundError("No USB device related to FTDI found in lsusb output.")
            
    except subprocess.CalledProcessError as e:
        print("Error running lsusb:", e.output)
        return None
"""


def find_tty_usb_device_id_dmesg():
    command = "sudo dmesg | grep tty"
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)

    print("output: ", output)
    
    # pattern = r"usb \d-\d:\sFTDI USB Serial Device converter now attached to (tty\w+)"
    pattern = r"usb \d-\d+\.\d+:\sFTDI USB Serial Device converter now attached to (tty\w+)"
    match = re.search(pattern, output)
    
    if match:
        device_id = match.group(1)
        print("device_id: ", device_id)
        return device_id
    else:
        print("Error running dmesg:", e.output)
        return None

    

def find_tty_usb_device_id():
    """
    # Try find_tty_usb_device_id_lsusb
    try:
        device_id = find_tty_usb_device_id_lsusb()
        return device_id
    except NoUSBDeviceFoundError:
        pass
    """

    # Try find_tty_usb_device_id_dmesg
    try:
        device_id = find_tty_usb_device_id_dmesg()
        return device_id
    except NoUSBDeviceFoundError:
        pass

    # Return None if no USB device is found
    return None


def scan_charge_controller():
    device_id = find_tty_usb_device_id()

    if device_id is None:
        raise Exception("Didn't find the device - please check if it's connected and please check the device ID")

    command = "sudo ./mpptemoncms/mpptemoncms -c mppt_config.conf -d /dev/" + device_id
    output_bytes = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    
    try:
        output = output_bytes.decode('utf-8')
    except UnicodeDecodeError:
        output = output_bytes.decode('latin-1')  # Use 'latin-1' as a more permissive encoding

    marker = "GET /input/post.json"
    json_start = output.find(marker)
    if json_start != -1:
        json_start = output.find("{", json_start)
        json_end = output.find("}", json_start) + 1
        json_data = output[json_start:json_end]

        json_data = re.sub(r'(\w+):', r'"\1":', json_data)
    
        parsed_json = json.loads(json_data)

        # Extract data into a more descriptive dictionary with formatting
        data = {
            "panel_voltage": "{:.3f}".format(parsed_json.get("vpv")),
            "panel_power": parsed_json.get("ppv"),
            "battery_voltage": "{:.3f}".format(parsed_json.get("v")),
            "battery_current": "{:.3f}".format(parsed_json.get("i")),
            "battery_yield_total": "{:.2f}".format(parsed_json.get("yt")),
            "battery_yield_today": "{:.2f}".format(parsed_json.get("yd")),
            "battery_yield_yesterday": "{:.2f}".format(parsed_json.get("yy")),
            "max_power_today": parsed_json.get("mpd"),
            "max_power_yesterday": parsed_json.get("mpy"),
            "charger_status": parsed_json.get("cs")
        }


        return data
    else:
        print("JSON data not found in output.")
        return None


def check_voltage(charge_controller):
    panel_data = charge_controller
    battery_voltage_str = panel_data["battery_voltage"]
    try:
        battery_voltage = float(battery_voltage_str)
        return battery_voltage
    except ValueError:
        print("Error converting battery voltage to numeric value:", battery_voltage_str)
        return 0.0  # Return a default value (you can adjust this as needed)


# charge_controller_data = scan_charge_controller()
"""
if charge_controller_data:
    print(json.dumps(charge_controller_data, indent=2))
"""
