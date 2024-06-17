# Intro

superbird should and could be a brilliant device with a compact package, good enough I/O and a soc better than Raspberry Pi 2 W (although without WiFi and ports)

Anyway, if you still think this will become e-waste for you, **you can for sure support this project by sending it to me :)**

**TRY EVERYTHING BELOW AT YOUR OWN RISK!!!**

**EXPERT USERS ONLY. If you don't know what you are doing, STOP**.

**Kernel repo**: https://github.com/alexcaoys/linux-superbird-6.6.y

## Support Matrix

**Driver Level**: https://linux-meson.com/hardware.html

**User Level**:
|                     |     |
|---------------------|-----|
|UART                 |Yes* |
|Keys                 |Yes  |
|Rotary               |Yes* |
|Touch                |Yes**|
|Ambient Light Sensor |Yes  |
|Audio In (PDM)       |Yes  |
|Bluetooth            |Yes* |
|USB                  |Yes  |
|Backlight            |Yes  |
|MIPI Display         |Partially  |
|Accel Sensor         |No (Not Found?)  |

\* : Driver tweak \
\*\* : Use old (vendor) driver

## Release
Compiled Kernel will be available on Kernel Repo [release](https://github.com/alexcaoys/linux-superbird-6.6.y/releases) section.

I will consider uploading my Buildroot rootfs to this release page. But Buildroot is pretty much a customizable system so do try it out on your own. **It's amazing!**

Armbian should be doable but I don't really have time/need for that for now.

Since Display is working partially, it's not really in working condition for all users. But you are welcome to try. Hopefully we can get this fix ASAP.

**Please Check RELEASE_NOTES.md for details.**

# Buildroot

https://buildroot.org/

There might be a lot of dependencies required by different package, google them should give you some clue.

I select custom kernel inside buildroot only to generate `/lib/modules`.

USB Gadget Ethernet (`g_ether`) is enabled automatically (Check `rootfs_overlay/etc/init.d/S49gether`) so you can `ssh root@172.16.42.2` after setting up the host ip properly (Check https://wiki.postmarketos.org/wiki/USB_Internet).

`cog -O renderer=gles` should work with display & touchscreen. Looks like `cog 0.19.1` (Not in Buildroot 2024.2) can work with touchscreen rotation, haven't tested yet. 

# Boot

- pyamlboot: https://github.com/superna9999/pyamlboot
- Restore partitions using superbird-tool: https://github.com/bishopdynamics/superbird-tool

In order for the display to work properly, we need to bypass `init_display` within u-boot, you can either 

- restore `envs/env_uboot.txt` using superbird-tool, which will cause stock firmware not working, but restore the stock env can bring it back, or 

- enter from USB mode -> `--burn_mode`, thanks @Fexiven noticing this ([our discussion here](https://github.com/alexcaoys/notes-superbird/issues/3)).

## Boot using stock partitions

set `active_slot=_b` and **clear dtbo_b partition**. Otherwise custom dtb won't be loaded.

Personally I create empty partitions for `dtbo_b` and `boot_b` partitions to flash into the device.

Restore new buildroot partition to `system_b` and use `envs/env_b.txt` in this repo to boot. 

I also created an Buildroot uInitrd image in case anything need an in-RAM system (repartitioning for example), please find it in Release and use `envs/env_initrd.txt` in this repo to boot.

I took parts from `superbird-tool` and wrote the script for boot custom images: 
Please check `amlogic_device.py`
    - use `python amlogic_device.py -c` to boot kernel + dtb specified in `__main__`
    - use `python amlogic_device.py -i` to boot kernel + dtb + uInitrd specified in `__main__`

## Boot from custom partitions

**W.I.P**

# Partitioning

Allow the unifreq kernel to read AML partition table: https://github.com/ophub/amlogic-s9xxx-armbian/issues/1109

**Below steps are NOT neccessary.**

- AML Partition Tables: https://7ji.github.io/embedded/2022/11/11/ept-with-ampart.html
- Tool: https://github.com/7Ji/ampart/tree/master
- Decrypt AML dtb: https://7ji.github.io/crack/2023/01/08/decrypt-aml-dtb.html

My backup ampart partitions output is in `ampart_partitions.txt`.

**REMEMBER TO BACKUP** dtb partition tables using `dd if=/dev/mmcblk2 of=dtb_part_dd.dump bs=256K skip=160 count=2`

**Repartitioning also requires a working system not on emmc, I will put working initramfs for that purpose on the Release page.**

According to the reference above, in order to repartition the emmc using the tool they provide, we need to extract and decrypt a vendor dts (not the one in dtbo partitions), and then replaced an encrypted dtb with the decrpyted one inside a reserved partition. 

But after doing so, the stock firmware won't boot at all (probably due to vendor u-boot restrictions).

Essentially if someone mess up the partitions and have no backup for that, the device will not work with the stock firmware at all. (by the way, looks like there's already [full backups](https://github.com/err4o4/spotify-car-thing-reverse-engineering/issues/30#issuecomment-2161567419), although a bit little bit hard to restore)

Because the kernel here can read the Amlogic partition tables, and 512MB system partition is enough at the current stage. I suggest everyone not to repartition the device before we have a fully functional kernel/system. 

# Kernel / Device Tree Tweaks

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

## IIO 

Looks like `st,lis2dh12-accel` is not working. I remember it's not in stock firmware as well, so this sensor may not be there after all.

`amstaos,tmd2772` Ambient Light Sensor / Prox Sensor is working perfectly.

## MIPI DSI Display

**W.I.P**

G12A MIPI DSI display driver should be in working condition on Linux 6.10.
This fork uses everything in `drivers/gpu/drm/meson` from Linux 6.10 and has modifications on the panel driver (`drivers/gpu/drm/panel/panel-sitronix-st7701.c`)

At the moment, some specific configs for ST7701S can display correct color and resolution. **But the refresh rate may not be 60Hz**. We are still working on it. Please check issue [#3](https://github.com/alexcaoys/notes-superbird/issues/3).

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

# IIO
`tmd2772` is within `/sys/bus/iio/devices`, could be 0 or 1, check `in_proximity0_raw` etc.

## Audio In

Check `rootfs_overlay/root/alsa.sh`

TODDR IN is fixed. PDM is 4. Use the below command to change the default.

`amixer cset name='TODDR_A SRC SEL' 'IN 4'`

Recording is working, post-processing might be needed. 

`arecord --channels=4 --format=S32_LE --duration=5 --rate=48000 --vumeter=mono --file-type=wav test.wav`

# Reference

## Linux Kernel
- Linux Meson: https://linux-meson.com/hardware.html
- Unifreq Kernel: https://github.com/unifreq/linux-6.6.y
- g_ether support: https://linuxlink.timesys.com/docs/wiki/engineering/HOWTO_Use_USB_Gadget_Ethernet
- Kernel Size Tuning: https://elinux.org/Kernel_Size_Tuning_Guide
- Superbird Stock Kernel: https://github.com/spsgsb/kernel-common

## U-Boot
- booti: https://docs.u-boot.org/en/v2021.04/usage/booti.html
- Amlogic boot: https://7ji.github.io/embedded/2022/11/11/amlogic-booting.html
- Stock u-boot: https://github.com/spsgsb/uboot
- kernel params: https://www.kernel.org/doc/html/v6.1/admin-guide/kernel-parameters.html
