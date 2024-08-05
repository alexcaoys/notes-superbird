
# Kernel / Device Tree Tweaks

Please check the commits in the [kernel repo](https://github.com/alexcaoys/linux-superbird-6.6.y). 

My dts for superbird: `arch/arm64/boot/dts/amlogic/meson-g12a-superbird.dts`

`make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- LOCALVERSION= Image dtbs`

Porting from old dts to new, watch out for field changes, \
eg. GPIO pinctrl: pins -> groups

## Support Matrix

**Driver Level**: https://linux-meson.com/hardware.html

**User Level**:
|                     |      |
|---------------------|------|
|UART                 |Yes*  |
|Keys                 |Yes   |
|Rotary               |Yes*  |
|Touch                |Yes** |
|Ambient Light Sensor |Yes   |
|Audio In (PDM)       |Yes   |
|USB (Device)         |Yes   |
|USB (Host)           |Yes   |
|Bluetooth            |Yes*  |
|Backlight            |Yes   |
|MIPI Display         |Partially*  |

\* : Driver tweak \
\*\* : Use old (vendor) driver

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

# u-boot

- [Radxa Zero u-boot Docs](https://docs.u-boot.org/en/latest/board/amlogic/radxa-zero.html)

OK, now I have the second rabbit hole here (partitioning being the first).

`fatload` and then `go` using a Radxa Zero mainline u-boot bin file actually works. \
**This makes Mainline Linux Kernel working, but without any noticable advantages.** 

Please check `uboot_envs/env_mainline_uboot.txt` for some mainline u-boot environments for booting the same thing as using `uboot_envs/env_full_custom.txt` on stock u-boot.

If anyone wants to do something using Mainline u-boot. You can simply build one using Radxa Zero `defconfig`. \
Hopefully this helps.

# Armbian

I took the radxa zero rootfs and successfully boot into Armbian.

By the way, you can not directly write the image to rootfs, the Armbian image is a disk image, not a partition dump. you need to mount the image (`sudo losetup -P /dev/loopX Armbian.img`) and create a partition image (`dd if=/dev/loopXp1 of=armbian_part.img bs=4M status=progress`) to write into your device. \
After that, you need to boot with initrd, copy /lib/modules/x.x.xx to armbian root.

Finally, it needs to have some tweaks before first boot. I disable first time login (`rm /root/.not_logged_in_yet`) and modify the default sshd_config to enable root login (same as Buildroot). 

After you log into root, `touch /root/.not_logged_in_yet` and `/usr/lib/armbian/armbian-firstlogin` to run first time login script. \
Essentially, since this is not built for superbird, you should expect that not everything works out of the box (GLES for example), but they do on Buildroot. \
As long as it can be boot into the system, I won't go into all the details from there. Buildroot will still be my focus. 

## g_ether
Add `modules-load=g_ether` to `bootargs.txt`. Modify `/etc/netplan/armbian-default.yaml` in rootfs.
```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    usb0:
      addresses:
        - 172.16.42.2/24
      nameservers:
        addresses:
          - 8.8.8.8
      routes:
        - to: default
          via: 172.16.42.1
```

# Reference

## Kernel
- Linux Meson: https://linux-meson.com/hardware.html
- Unifreq Kernel: https://github.com/unifreq/linux-6.6.y
- Superbird Stock Kernel: https://github.com/spsgsb/kernel-common
- g_ether support: https://linuxlink.timesys.com/docs/wiki/engineering/HOWTO_Use_USB_Gadget_Ethernet
- Kernel Size Tuning: https://elinux.org/Kernel_Size_Tuning_Guide

## u-Boot
- Stock u-boot: https://github.com/spsgsb/uboot
- Amlogic Boot: https://7ji.github.io/embedded/2022/11/11/amlogic-booting.html
- booti: https://docs.u-boot.org/en/v2021.04/usage/booti.html

