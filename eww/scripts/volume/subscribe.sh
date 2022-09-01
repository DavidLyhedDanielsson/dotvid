#!/bin/sh

pactl subscribe | grep --line-buffered "'change' on sink #$(pamixer --get-default-sink | sed 1d | cut -c 1-2)" | xargs -n1 $VOLUME_DIR/update_volume.sh
