#!/bin/sh

STEPS=100           # Number of brightness transition steps
STEP_DELAY=0.01     # Delay between steps
PAUSE=15            # Delay between ambient measurements

CHECK_SCREEN_STATE=1

# Overall delay:
# STEPS * STEP_DELAY + PAUSE

# Init ALS IIO
if [ -e /sys/bus/iio/devices/iio:device0/in_intensity0_raw ]; then
    echo 16 > /sys/bus/iio/devices/iio:device0/in_intensity0_calibscale
    ALS_IIO=/sys/bus/iio/devices/iio:device0/in_intensity0_raw
else
    echo 16 > /sys/bus/iio/devices/iio:device1/in_intensity0_calibscale
    ALS_IIO=/sys/bus/iio/devices/iio:device1/in_intensity0_raw
fi

# Init backlight
BACKLIGHT=/sys/class/backlight/backlight

OUT_BR="$BACKLIGHT/brightness"
ACTUAL_BR="$BACKLIGHT/actual_brightness"

MIN=64
MAX=$(cat "$BACKLIGHT/max_brightness")
RANGE=$((MAX - MIN))

MIN_AMBIENT_DIFF=4

# Reset brightness
echo "$MIN" > "$OUT_BR"
last_ambient=0

while true; do
    sleep "$PAUSE"

    if [ "$CHECK_SCREEN_STATE" -ne 0 ]; then
        if [ "$(cat "$ACTUAL_BR")" -eq 0 ]; then
            echo "Screen is off, skipping"
            continue
        fi
    fi

    ambient=$(cat "$ALS_IIO")
    ambient_diff=$((last_ambient - ambient))

    # Absolute value
    if [ "$ambient_diff" -lt 0 ]; then
        ambient_diff=$((-ambient_diff))
    fi

    echo "Ambient value: $ambient"
    echo "Ambient diff: $ambient_diff"

    if [ "$ambient_diff" -lt "$MIN_AMBIENT_DIFF" ]; then
        echo "Skipping change"
        continue
    fi

    last_ambient=$ambient

    curr_brightness=$(cat "$ACTUAL_BR")
    new_brightness=$((MIN + RANGE * ambient / 1024))

    incr=$(((new_brightness - curr_brightness) / STEPS))

    if [ "$incr" -eq 0 ]; then
        if [ "$new_brightness" -gt "$curr_brightness" ]; then
            incr=1
        elif [ "$new_brightness" -lt "$curr_brightness" ]; then
            incr=-1
        else
            incr=0
        fi
    fi

    if [ "$incr" -ne 0 ]; then
        br=$curr_brightness

        while :; do
            echo "$br" > "$OUT_BR"
            sleep "$STEP_DELAY"

            if [ "$incr" -gt 0 ]; then
                [ "$br" -ge "$new_brightness" ] && break
            else
                [ "$br" -le "$new_brightness" ] && break
            fi

            br=$((br + incr))
        done
    fi

    echo "$new_brightness" > "$OUT_BR"
    echo "Brightness set: $new_brightness"
done