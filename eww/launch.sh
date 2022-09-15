#!/bin/bash

echo "Launching ewwbar!"

export PATH=$HOME/.local/bin:$PATH

export VOLUME_DIR=/home/$USER/.config/eww/scripts/volume
export BATTERY_DIR=/home/$USER/.config/eww/scripts/battery
export WIFI_DIR=/home/$USER/.config/eww/scripts/wifi
export WORKSPACE_DIR=/home/$USER/.config/eww/scripts/workspace
export DISK_DIR=/home/$USER/.config/eww/scripts/disk

kill_all() {
    pid=$(pgrep -f $1)
    if [ -n "${pid}" ]; then
        echo $pid | xargs -n1 kill -9
    else
        echo "$1 not running"
    fi
}

kill_all "volume.py"
kill_all "wifi.py"
kill_all "workspace.py"

python3 /home/davidwithrice/.config/dotvid/eww/scripts/volume/volume.py &
python3 /home/davidwithrice/.config/dotvid/eww/scripts/wifi/wifi.py &
python3 /home/davidwithrice/.config/dotvid/eww/scripts/workspace/workspace.py &

$HOME/.local/bin/eww daemon

eww update volume_percent=$($VOLUME_DIR/get.sh)
eww update wifi_status="$($WIFI_DIR/get.sh)"
python3 /home/davidwithrice/.config/dotvid/eww/scripts/workspace/workspace.py --get

$HOME/.local/bin/eww open bar

echo "Ewwbar done"
