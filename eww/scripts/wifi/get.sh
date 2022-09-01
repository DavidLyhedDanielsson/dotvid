#!/bin/sh

interface=$(cat /proc/net/wireless | tail -n +3 | cut -d ':' -f1)

if [ ! "$interface" ]; then
    name=""
    status="disconnected"
else
    name=$(iwgetid -r)
    status="connected"
fi

echo "{\"status\": \"$status\", \"name\": \"$name\"}"