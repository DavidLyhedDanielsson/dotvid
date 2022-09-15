#!/bin/sh

echo $($WORKSPACE_DIR/get.sh)

function handle {
    action=$(echo $1 | rg -o "(createworkspace|destroyworkspace)")
    if [[ -n $action ]]; then
        echo $($WORKSPACE_DIR/get.sh)
    fi
}

#socat - UNIX-CONNECT:/tmp/hypr/$(echo $HYPRLAND_INSTANCE_SIGNATURE)/.socket2.sock | while read line; do handle $line; done
socat -u UNIX-CONNECT:/tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock - | while read -r line; do handle "$line"; done
