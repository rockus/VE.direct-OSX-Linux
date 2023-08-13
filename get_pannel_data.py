import subprocess
import json
import re


def find_tty_usb_device_id():
    command = "sudo dmesg | grep tty"
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    
    pattern = r"usb \d-\d:\sFTDI USB Serial Device converter now attached to (tty\w+)"
    match = re.search(pattern, output)
    if match:
        device_id = match.group(1)
        return device_id
    else:
        return None

def scan_charge_controller():
    device_id = find_tty_usb_device_id()

    if device_id is None:
        raise Exception("Didn't find the device - please check if it's connected and please check the device ID")

    command = "sudo ./mpptemoncms/mpptemoncms -c mppt_config.conf -d /dev/" + device_id
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)

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

charge_controller_data = scan_charge_controller()
"""
if charge_controller_data:
    print(json.dumps(charge_controller_data, indent=2))
"""
