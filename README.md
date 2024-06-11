# Intro

superbird should and could be a brilliant device with a compact package, good enough I/O and a soc better than Raspberry Pi 2 W (although without WiFi and ports)

Anyway, if you still think this will become e-waste for you, **you can for sure support this project by sending it to me :)**

**Kernel repo**: https://github.com/alexcaoys/linux-superbird-6.6.y

## Support Matrix

**Driver Level**: https://linux-meson.com/hardware.html

**User Level**:
|                    |     |
|--------------------|-----|
|UART                |Yes* |
|Keys                |Yes  |
|Rotary              |Yes* |
|Touch               |Yes**|
|Ambient Light Sensor|Yes  |
|Audio In (PDM)      |Yes  |
|Bluetooth           |Yes* |
|USB                 |Yes  |
|Backlight           |Yes  |
|MIPI Display        |WIP  |

\* : Driver tweak \
\*\* : Use old (vendor) driver

## Release

**Everything is TRY AT YOUR OWN RISK!!!**

**EXPERT USERS ONLY**. If you don't know what you are doing, **STOP**.

Since Display is not working properly, it's not really in working condition for any users. But you are welcome to try. Hopefully we can get this fix ASAP.

Compiled Kernel will be available on Kernel Repo [release](https://github.com/alexcaoys/linux-superbird-6.6.y/releases) section.

I will consider uploading my Buildroot rootfs to this release page. But Buildroot is pretty much a customizable system so do try it out on your own. **It's amazing!**

Armbian should be doable but I don't really have time/need for that for now.

# Reference

## Linux Kernel
- Superbird Kernel: https://github.com/spsgsb/kernel-common
- Linux Meson: https://linux-meson.com/hardware.html
- Unifreq Kernel: https://github.com/unifreq/linux-6.6.y
- g_ether support: https://linuxlink.timesys.com/docs/wiki/engineering/HOWTO_Use_USB_Gadget_Ethernet
- Kernel Size Tuning: https://elinux.org/Kernel_Size_Tuning_Guide

## U-Boot
- booti: https://docs.u-boot.org/en/v2021.04/usage/booti.html
- Amlogic boot: https://7ji.github.io/embedded/2022/11/11/amlogic-booting.html
- Stock u-boot: https://github.com/spsgsb/uboot
- kernel params: https://www.kernel.org/doc/html/v6.1/admin-guide/kernel-parameters.html

## Partitioning

Allow the unifreq kernel to read AML partition table: https://github.com/ophub/amlogic-s9xxx-armbian/issues/1109

**Below steps are NOT neccessary.**

- AML Partition Tables: https://7ji.github.io/embedded/2022/11/11/ept-with-ampart.html
- Tool: https://github.com/7Ji/ampart/tree/master
- Decrypt AML dtb: https://7ji.github.io/crack/2023/01/08/decrypt-aml-dtb.html

**REMEMBER TO BACKUP** dtb partition tables using `dd if=/dev/mmcblk2 of=dtb_part_dd.dump bs=256K skip=160 count=2`

`run storeboot` only works with the stock dtb above.

Follow steps above, decrypt and push the dtb partition tables to reserve partition.

# Buildroot

I select custom kernel inside buildroot only to generate `/lib/modules`.

USB Gadget Ethernet (`g_ether`) is enabled automatically (Check `rootfs_overlay/etc/init.d/S49gether`) so you can `ssh root@172.16.42.2` after setting up the host ip properly.

`cog -O renderer=gles` should work with display & touchscreen. Looks like `cog 0.19.1` (Not in Buildroot 2024.2) can work with touchscreen rotation, haven't tested yet. 

# Boot

- pyamlboot: https://github.com/superna9999/pyamlboot
- Restore partitions using superbird-tool: https://github.com/bishopdynamics/superbird-tool

set `active_slot=_b` and **clear dtbo_b partition**. Otherwise custom dtb won't be loaded.

Personally I create empty partitions for `dtbo_b` and `boot_b` partitions to flash into the device.
Restore new buildroot partition to `system_b` and use `env_b.txt` in this repo to boot. 

I took parts from `superbird-tool` and wrote the script for boot custom kernel+dtb: check `amlogic_device.py`, use `python amlogic_device.py -c` to boot the files specified in `__main__`

# Kernel / Device Tree

Please check the commits in the kernel repo. 

My dts for superbird: `arch/arm64/boot/dts/amlogic/meson-g12a-superbird.dts`

Porting from old dts to new, watch out for field changes, \
eg. GPIO pinctrl: pins -> groups

## Rotary Encoder

GPIO IRQ: https://forum.odroid.com/viewtopic.php?t=40322

IRQ_TYPE_EDGE_BOTH: use stock irq

## Touch Screen

Use stock driver tlsc6x

## Bluetooth

Need modifications to `meson_uart.c` and bluetooth drivers. For dts, bluetooth under uart is not working.

Check `rootfs_overlay/root/bt.sh`
```sh
gpioset 0 82=1  # Power on GPIOX_17
btattach -P bcm -B /dev/ttyAML6 &
bluetoothctl
gpioset 0 82=0  # Power off
```

## MIPI DSI Display

**WIP**

G12A MIPI DSI display driver should be in working condition on Linux 6.10.
This fork uses everything in `drivers/gpu/drm/meson` from Linux 6.10 and has modifications on the panel driver (`drivers/gpu/drm/panel/panel-sitronix-st7701.c`)

Display works but the panel is still tinted (possibly bitshift), so it's still WIP.

# Testing

## Mount debugfs
```sh
mount -t debugfs none /sys/kernel/debug
```

## Check pins
```sh
cat /sys/kernel/debug/pinctrl/ff634400.bus\:pinctrl@40-pinctrl-meson/pinconf-pins
```

## Button / Rotary / Touch Test
```sh
libinput debug-events
```

## Backlight
Not integrated into lcd for now
```sh
cat /sys/class/backlight/backlight/brightness
echo 0 > /sys/class/backlight/backlight/brightness
```

## Audio In

Check `rootfs_overlay/root/alsa.sh`

TODDR IN is fixed. PDM is 4. Use the below command to change the default.

`amixer cset name='TODDR_A SRC SEL' 'IN 4'`

Recording is working, post-processing might be needed. 

`arecord --channels=4 --format=S32_LE --duration=5 --rate=48000 --vumeter=mono --file-type=wav test.wav`
