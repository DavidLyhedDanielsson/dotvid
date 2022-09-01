#!/bin/sh

per="$(cat '/sys/class/power_supply/BAT0/capacity')"

if [ "$per" -gt "90" ]; then
	icon=""
elif [ "$per" -gt "80" ]; then
	icon=""
elif [ "$per" -gt "70" ]; then
	icon=""
elif [ "$per" -gt "60" ]; then
	icon=""
elif [ "$per" -gt "50" ]; then
	icon=""
elif [ "$per" -gt "40" ]; then
	icon=""
elif [ "$per" -gt "30" ]; then
	icon=""
elif [ "$per" -gt "20" ]; then
	icon=""
elif [ "$per" -gt "10" ]; then
	icon=""
elif [ "$per" -gt "0" ]; then
	icon=""
else
    icon=""
fi

acpi -b | rg '(((?:Not c|Disc|C)harging).*?([0-9]+)%(?:, ([0-9:]{5}))?)' -or '["$2", "$3", "$4", "'${icon}'"]'