
# Kernel / Device Tree Tweaks

Please check the commits in the [kernel repo](https://github.com/alexcaoys/linux-superbird-6.6.y). 

My dts for superbird: `arch/arm64/boot/dts/amlogic/meson-g12a-superbird.dts`

Porting from old dts to new, watch out for field changes, \
eg. GPIO pinctrl: pins -> groups

## MIPI DSI Display

**Patially Working**

[ST7701S White Paper](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/imx-processors/134161/3/ST7701S_SPEC_Preliminary%20V0.1.pdf) \
[Latest Patch for MIPI DSI](https://patchwork.kernel.org/project/linux-arm-kernel/cover/20240403-amlogic-v6-4-upstream-dsi-ccf-vim3-v12-0-99ecdfdc87fc@linaro.org/)

G12A MIPI DSI display driver should be in working condition on Linux 6.10. \
This fork uses everything in `drivers/gpu/drm/meson` from Linux 6.10 and has modifications on the panel driver (`drivers/gpu/drm/panel/panel-sitronix-st7701.c`)

At the moment, some specific configs for ST7701S can display correct color and resolution. **But the refresh rate may not be 60Hz**. We are still working on it. Please check issue [#3](https://github.com/alexcaoys/notes-superbird/issues/3).

## Bluetooth

Need modifications to `meson_uart.c` and bluetooth drivers. For dts, bluetooth under uart is not working.

## Touch Screen

Use stock driver tlsc6x

## GPIO Keys / Rotary Encoder

- gpio-keys-polled: https://www.kernel.org/doc/Documentation/devicetree/bindings/input/gpio-keys-polled.txt
- Rotary Encoder: https://www.kernel.org/doc/Documentation/devicetree/bindings/input/rotary-encoder.txt
- GPIO IRQ: https://forum.odroid.com/viewtopic.php?t=40322

IRQ_TYPE_EDGE_BOTH: use stock irq

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

- Linux Meson: https://linux-meson.com/hardware.html
- Unifreq Kernel: https://github.com/unifreq/linux-6.6.y
- Superbird Stock Kernel: https://github.com/spsgsb/kernel-common
- g_ether support: https://linuxlink.timesys.com/docs/wiki/engineering/HOWTO_Use_USB_Gadget_Ethernet
- Kernel Size Tuning: https://elinux.org/Kernel_Size_Tuning_Guide

