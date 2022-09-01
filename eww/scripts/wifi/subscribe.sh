#!/bin/sh

nmcli device monitor | rg --line-buffered "(wlan0: (disconnected|connected))" -or '$2' | xargs -I{} eww update "wifistatus={\"status\": \"{}\", \"name\": \"$(iwgetid -r)\"}"