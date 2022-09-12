#!/bin/sh

interface=$(cat /proc/net/wireless | tail -n +3 | cut -d ':' -f1)

if [ ! "$interface" ]; then
    name=""
    connected="false"
else
    name=$(iwgetid -r)
    connected="true"
fi

echo "{\"connected\": $connected, \"name\": \"$name\"}"