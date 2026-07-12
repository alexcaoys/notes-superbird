
# Kernel / Device Tree Tweaks

Based on Linux 6.18, all the patches are in the `patches` folder, everything should work just like the stock firmware. \
dts for superbird: `configs/linux-6.18/meson-g12a-superbird.dts` \
And follow the general steps here:
```sh
cp -r ./patches ~/linux-6.18.y
cp ./configs/linux-6.18/meson-g12a-superbird.dts ~/linux-6.18.y/arch/arm64/boot/dts/amlogic/
cp ./configs/linux-6.18/defconfig ~/linux-6.18.y/.config
cd ~/linux-6.18.y
git apply ./patches/*.patch
```
This is for native ARM64 compile:
```sh
make menuconfig
# to build ARM64 Image
make
```

CROSS_COMPILE (on Ubuntu):
```sh
sudo apt install build-essential gcc-aarch64-linux-gnu

make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
# to build ARM64 Image
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
```

## Support Matrix

**Driver Level**: https://linux-meson.com/hardware.html

**User Level**:
|                     |      |
|---------------------|------|
|MIPI Display         |Yes*  |
|UART                 |Yes*  |
|IRQ Double Edge      |Yes** |
|Keys                 |Yes   |
|Rotary               |Yes   |
|Touch                |Yes** |
|Ambient Light Sensor |Yes   |
|Audio In (PDM)       |Yes   |
|USB (Device)         |Yes   |
|USB (Host)           |Yes   |
|Bluetooth            |Yes*  |
|Backlight            |Yes   |

\* : Driver tweak \
\*\* : Use old (vendor) driver

## MIPI DSI Display

The newest patch supports the correct timing with 60Hz refresh rate. The key is actually some settings in Meson DSI drivers. Display panel config itself is also very important here. (`drivers/gpu/drm/panel/panel-sitronix-st7701.c`)

## Bluetooth

Need modifications to `meson_uart.c` and bluetooth drivers. The newest patch can bring up Bluetooth at boot, more or less aligning with Mainline Bluetooth like Radxa Zero.

## Touch Screen

Use stock driver tlsc6x

## GPIO Keys / Rotary Encoder

- gpio-keys-polled: https://www.kernel.org/doc/Documentation/devicetree/bindings/input/gpio-keys-polled.txt
- Rotary Encoder: https://www.kernel.org/doc/Documentation/devicetree/bindings/input/rotary-encoder.txt

IRQ_TYPE_EDGE_BOTH: need stock irq double edge hacks.

## IIO 

ALS Sensor: https://www.kernel.org/doc/Documentation/devicetree/bindings/iio/light/tsl2772.txt

`amstaos,tmd2772` Ambient Light Sensor / Prox Sensor is working perfectly. \
Only need a bit calibration. `in_intensity0_calibscale` and `in_proximity0_calibscale`

Stock Values:
```
in_illuminance0_calibrate

in_illuminance0_calibscale_available
1 8 16 120
in_illuminance0_input

in_illuminance0_integration_time
0.111
in_illuminance0_integration_time_available
.00272 - .696
in_illuminance0_lux_table
13218,130,262,17592,92,169,0,0,0
in_illuminance0_target_input
150
in_intensity0_calibbias
1000
in_intensity0_calibscale
2
in_intensity0_raw

in_intensity1_raw

in_proximity0_calibrate

in_proximity0_calibscale
2
in_proximity0_calibscale_available
1 2 4 8
```

Looks like `st,lis2dh12-accel` is not working. this sensor may not be there. ([It's not there](https://github.com/alexcaoys/notes-superbird/issues/6))

## Testing

```sh
# Mount debugfs
mount -t debugfs none /sys/kernel/debug
# Check pins
cat /sys/kernel/debug/pinctrl/ff634400.bus\:pinctrl@40-pinctrl-meson/pinconf-pins
# Button / Rotary / Touch Test
libinput debug-events
# ALS Sensor, could also be iio\:device1
cat /sys/bus/iio/devices/iio\:device0/in_intensity0_raw 
# Backlight, brightness 0 to 255
cat /sys/class/backlight/backlight/brightness
echo 0 > /sys/class/backlight/backlight/brightness
```

# Reference

## Kernel
- Linux Meson: https://linux-meson.com/hardware.html
- Stock Kernel: https://github.com/spsgsb/kernel-common
- g_ether support: https://linuxlink.timesys.com/docs/wiki/engineering/HOWTO_Use_USB_Gadget_Ethernet
- Kernel Size Tuning: https://elinux.org/Kernel_Size_Tuning_Guide
