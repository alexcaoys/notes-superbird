# Linux Kernel

- Superbird Kernel: https://github.com/spsgsb/kernel-common
- Linux Meson: https://linux-meson.com/hardware.html
- Unifreq Kernel: https://github.com/unifreq/linux-6.6.y
- g_ether support: https://linuxlink.timesys.com/docs/wiki/engineering/HOWTO_Use_USB_Gadget_Ethernet
- Kernel Size Tuning: https://elinux.org/Kernel_Size_Tuning_Guide

# U-Boot

- booti: https://docs.u-boot.org/en/v2021.04/usage/booti.html
- Amlogic boot: https://7ji.github.io/embedded/2022/11/11/amlogic-booting.html
- Stock u-boot: https://github.com/spsgsb/uboot
- kernel params: https://www.kernel.org/doc/html/v6.1/admin-guide/kernel-parameters.html

# Partitions

- Allow the unifreq kernel to read AML partition table: https://github.com/ophub/amlogic-s9xxx-armbian/issues/1109

**Below steps are NOT neccessary.**

- AML Partition Tables: https://7ji.github.io/embedded/2022/11/11/ept-with-ampart.html
- Tool: https://github.com/7Ji/ampart/tree/master
- Decrypt AML dtb: https://7ji.github.io/crack/2023/01/08/decrypt-aml-dtb.html

BACKUP dtb partition tables using `dd if=/dev/mmcblk2 of=dtb_part_dd.dump bs=256K skip=160 count=2`

`run storeboot` only works with the stock dtb above.

Follow steps above, decrypt and push the dtb partition tables to reserve partition.

# Buildroot

I select custom kernel inside buildroot only to generate `/lib/modules`.

USB Gadget Ethernet (`g_ether`) is enabled automatically so you can `ssh root@172.16.42.2` after setting up the host ip properly.

`cog -O renderer=gles` should work with display & touchscreen.

# Boot

- Restore partitions by superbird-tool: https://github.com/bishopdynamics/superbird-tool
- pyamlboot: https://github.com/superna9999/pyamlboot

set `active_slot=_b` and **clear dtbo_b partition**. Otherwise custom dtb won't be loaded.

Personally I create empty partitions for `dtbo_b` and `boot_b` partitions.
restore new buildroot partition to `system_b` and use `env_b.txt` in this repo. 

I took parts from `superbird-tool` and wrote the script for boot custom kernel+dtb: check `amlogic_device.py`, use `python amlogic_device.py -c` to boot the files specified in `__main__`

# dtb / dts
Watch out for field changes
eg. 
- GPIO pinctrl: pins -> groups

# Mount debugfs
```sh
mount -t debugfs none /sys/kernel/debug
```
# Check pins
```sh
cat /sys/kernel/debug/pinctrl/ff634400.bus\:pinctrl@40-pinctrl-meson/pinconf-pins
```

# Rotary Encoder

GPIO IRQ: https://forum.odroid.com/viewtopic.php?t=40322

IRQ_TYPE_EDGE_BOTH: use stock irq

# Touch Screen

Use stock driver tlsc6x

# Button / Rotary / Touch Test
```sh
libinput debug-events
```

# Sound

TODDR IN is fixed. PDM is 4. Use the below command to change the default.
`amixer cset name='TODDR_A SRC SEL' 'IN 4'`
Recording is working, post-processing is needed. 
`arecord --channels=4 --format=S32_LE --duration=5 --rate=48000 --vumeter=mono --file-type=wav test.wav`

# Bluetooth

Need modifications to `meson_uart.c` and bluetooth drivers. For dts, bluetooth under uart is not working.
```sh
gpioset 0 82=1  # Power on GPIOX_17
btattach -P bcm -B /dev/ttyAML6 &
bluetoothctl
gpioset 0 82=0  # Power off
```

# Backlight
Not integrated into lcd for now
```sh
cat /sys/class/backlight/backlight/brightness
echo 0 > /sys/class/backlight/backlight/brightness
```