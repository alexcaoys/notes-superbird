killall btattach
gpioset 0 82=0
sleep 1
gpioset 0 82=1  # Power on GPIOX_17
sleep 1
btattach -P bcm -B /dev/ttyAML6 &

if command -v bluealsa &> /dev/null
then
    sleep 1
    bluealsa -p a2dp-source -p a2dp-sink &  # Set up bluetooth audio
    echo 'REMEMBER TO SET .asoundrc for Bluetooth Audio'
fi
