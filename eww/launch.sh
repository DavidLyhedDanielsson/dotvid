#!/bin/bash

export VOLUME_DIR=/home/$USER/.config/eww/scripts/volume
export BATTERY_DIR=/home/$USER/.config/eww/scripts/battery
export WIFI_DIR=/home/$USER/.config/eww/scripts/wifi

pregp -P $(pgrep -f "scripts/wifi/subscribe.sh") | xargs -I{} kill {};pgrep -f "scripts/wifi/subscribe.sh" | xargs -I{} kill {}; setsid $WIFI_DIR/subscribe.sh &
pgrep -P $(pgrep -f "scripts/volume/subscribe.sh") | xargs -I{} kill {}; pgrep -f "scripts/volume/subscribe.sh" | xargs -I{} kill {}; setsid $VOLUME_DIR/subscribe.sh &

eww daemon

eww update volume_percent=$($VOLUME_DIR/get.sh)
eww update wifistatus="$($WIFI_DIR/get.sh)"

eww open bar
