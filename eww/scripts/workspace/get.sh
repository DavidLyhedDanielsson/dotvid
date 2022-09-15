#!/bin/sh

hyprctl -j workspaces | jq '[.[].id]'
