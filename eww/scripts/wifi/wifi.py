import subprocess
import json


def update_status(connected, ssid=""):
    command = {
        "connected": connected,
        "name": ssid
    }
    subprocess.run(
        ["eww", "update", "wifi_status=" + json.dumps(command)])


try:
    proc = subprocess.Popen(["nmcli", "monitor"], stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if b"is now the primary connection" in line:
            ssid = line.split()[0].decode("utf-8")[1:-1]
            update_status(True, ssid)
        elif b"wlan0: disconnected" in line:
            update_status(False, ssid)
except Exception as e:
    print(e)
