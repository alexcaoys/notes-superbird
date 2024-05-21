killall btattach
gpioset 0 82=0
sleep 1
gpioset 0 82=1
sleep 1
btattach -P bcm -B /dev/ttyAML6 &
