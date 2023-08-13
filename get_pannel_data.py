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

    if device_id == None:
        raise Exception("Didn't find the device - please check if it's connected and please check the device ID")

    # Run the command and capture the output
    # command = "sudo ./mpptemoncms/mpptemoncms -c mppt_config.conf -d /dev/ttyUSB3"
    command = "sudo ./mpptemoncms/mpptemoncms -c mppt_config.conf -d /dev/" + device_id
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)

    # Find the line containing the JSON data using a marker
    marker = "GET /input/post.json"
    json_start = output.find(marker)
    if json_start != -1:
        json_start = output.find("{", json_start)
        json_end = output.find("}", json_start) + 1
        json_data = output[json_start:json_end]

        # Convert the non-standard keys to valid JSON format
        json_data = re.sub(r'(\w+):', r'"\1":', json_data)
    
        # Parse the JSON data
        parsed_json = json.loads(json_data)
        print(json.dumps(parsed_json, indent=2))  # Print the JSON in a formatted way
    else:
        print("JSON data not found in output.")

scan_charge_controller()


"""

# Terminology:


  MPPT EMONCMS v2.02 (c)2015,2016 Oliver Gerler (rockus@rockus.at)

  date : Sun Aug 13 19:23:11 2023

charger:
  type: *UNKNOWN*
  fw  : v1.59
  ser : HQ2146CMFMK

panel:
  vpv : 15.080V
 [ipv :  0.000A]
  ppv :   0W
battery:
  v   : 12.700V
  i   : -0.830A
 [p   : -10.541W]
load:
 [v   : 12.700V (same voltage as battery)]
  il  :  0.800A
 [pl  : 10.160W
]charger status:
  cs  : Off
  err : No error
  load: On
  yield total         :   0.06kWh
  yield today         :   0.00kWh [  0.00Ah @ 13V nom.]
  yield yesterday     :   0.00kWh [  0.00Ah @ 13V nom.]
  max. power today    :    1W
  max. power yesterday:    0W
  hsds: 26

Note: values in square brackets [] are calculated by this tool,
      not in the charger.

256
GET /input/post.json?node="MySolarController"&json={vpv:15.080,ppv:0,v:12.700,i:-0.830,yt:0.06,yd:0.00,yy:0.00,mpd:1,mpy:0,cs:0}&apikey=58b2624934cbfbd3388b88b4e5253256 HTTP/1.1
Host: emoncms.org
User-Agent: MPPT EMONCMS v2.02
Connection: keep-alive


send: 256
Closing down.

"""
