# Intro

**superbird** (Spotify Car Thing) should and could be a brilliant device with a compact package, good enough I/O and a soc better than Raspberry Pi 2 W (although without WiFi and ports). Please keep in mind that this is an embedded device, don't expect it to solve any complicated tasks!

Anyway, if you still think this will become e-waste for you, **you can for sure support this project by sending it to me :)**

**TRY EVERYTHING BELOW AT YOUR OWN RISK!!!**

**EXPERT USERS ONLY. If you don't know what you are doing, STOP**.

**Kernel repo**: https://github.com/alexcaoys/linux-superbird-6.6.y

## Release

**Please Check RELEASE_NOTES.md for details.**

Compiled Kernel will be available on Kernel Repo [release](https://github.com/alexcaoys/linux-superbird-6.6.y/releases) section.

Since display is only working partially, I don't consider this as good for all users. But you are welcome to try. Hopefully we can get this fix ASAP.

I will consider uploading my Buildroot rootfs to this release page. But Buildroot is pretty much a customizable system so do try it out on your own. **It's amazing!**


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
|Bluetooth            |Yes*  |
|USB                  |Yes   |
|Backlight            |Yes   |
|MIPI Display         |Partially*  |
|GPIO LED             |Where is it?  |
|Accel Sensor         |Dev Not Found?  |

\* : Driver tweak \
\*\* : Use old (vendor) driver

# Boot

- pyamlboot: https://github.com/superna9999/pyamlboot
- Restore partitions using superbird-tool: https://github.com/bishopdynamics/superbird-tool
- Amlogic Boot: https://7ji.github.io/embedded/2022/11/11/amlogic-booting.html

In order for the display color to work properly, we need to bypass `init_display` within u-boot, you can either 

- restore `envs/env_full_dualboot.txt` using superbird-tool `--send_full_env` feature, or

- enter from USB mode and then enter superbird-tool `--burn_mode`

Thanks @Fexiven for noticing this ([our discussion here](https://github.com/alexcaoys/notes-superbird/issues/3)).

I took parts from `superbird-tool` and wrote the script for booting custom stuff: Please check `amlogic_device.py`.

## Boot using initrd

I created an Buildroot uInitrd image in case anything need an in-RAM system (repartitioning for example), please find it in Release and use `envs/env_initrd.txt` in this repo to boot.

Please use `python amlogic_device.py -i ENV_FILE KERNEL_FILE INITRD_FILE DTB_FILE` to boot kernel + dtb + uInitrd from host.

## Boot into stock partitions

set `active_slot=_b` and **clear dtbo_b partition**. Otherwise custom dtb won't be loaded.

1. Create empty `dtbo_b` and `boot_b` partitions by `dd` and restore to device.
2. Restore new buildroot partition to `system_b`.
3. Use `envs/env_b.txt` in this repo to boot. (`python amlogic_device.py -c ENV_FILE KERNEL_FILE DTB_FILE` to boot kernel + dtb from host)

## Boot into custom partitions

After repartitioning and restoring the rootfs as below. 

Use `envs/env_p2.txt` in this repo to boot. 

- `python amlogic_device.py -c ENV_FILE KERNEL_FILE DTB_FILE` to boot kernel + dtb from host, **OR**
- Using `fatload` to load kernel and dtb from `mmcblk2p1` and `python amlogic_device.py -m ENV_FILE` to boot. **OR**
- Send `env/env_full_custom.txt` to the device. Button 4 for burn mode, Normally it will load envs from `bootargs.txt` within `mmcblk2p1` and then boot into `mmcblk2p2` using `Image` and `superbird.dtb` from `mmcblk2p1`.

## After boot

Creating a swapfile can relief some pressure on memory. (https://linuxize.com/post/create-a-linux-swap-file/)

USB Gadget Ethernet (`g_ether`) is enabled automatically (Check `rootfs_overlay/etc/init.d/S49gether`) on Buildroot so you can `ssh root@172.16.42.2` after setting up the host ip (https://wiki.postmarketos.org/wiki/USB_Internet) properly. Here's a handy script:
```sh
INTERFACE=usb0

sudo ip address add dev $INTERFACE 172.16.42.1/24
sudo ip link set $INTERFACE up

if sudo iptables -L | grep 172.16.42.0; then
  echo "iptables rules exist"
else
  sudo sysctl net.ipv4.ip_forward=1

  sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  sudo iptables -A FORWARD -s 172.16.42.0/24 -j ACCEPT
  sudo iptables -A POSTROUTING -t nat -j MASQUERADE -s 172.16.42.0/24
  sudo iptables-save
fi

ssh root@172.16.42.2
```

# Partitioning

Allow the unifreq kernel to read AML partition table: https://github.com/ophub/amlogic-s9xxx-armbian/issues/1109

## Repartitioning

- AML Partition Tables: https://7ji.github.io/embedded/2022/11/11/ept-with-ampart.html
- Decrypt AML dtb: https://7ji.github.io/crack/2023/01/08/decrypt-aml-dtb.html
- Tool: https://github.com/7Ji/ampart/tree/master

**Remember to backup**

[full reserved partition backup](https://github.com/err4o4/spotify-car-thing-reverse-engineering/issues/30#issuecomment-2161567419) \
My backup ampart partitions output is in `ampart_partitions.txt`.

0. Please follow the [Decrypt AML dtb](https://7ji.github.io/crack/2023/01/08/decrypt-aml-dtb.html) to get the decrypted dtb from stock firmware. I uploaded one but it's recommended you do that using your own device. 
1. Use **uInitrd** to boot. `ampart` binary is already included under the `/root`, `ssh root@172.16.42.2` into the system. You should be able to use `scp` to transfer any files needed between host and superbird, `nfs` could also work.
2. Backup bootloader and encrypted dtb using 
    ```
    dd if=/dev/mmcblk2 of=bootloader.img bs=1M count=4
    dd if=/dev/mmcblk2 of=stock_dtb.img bs=256K skip=160 count=2
    ```
3. Copy the backups back to the host. 
4. Restore decrypted dtb using 
    ```
    dd if=decrypted.dtb of=/dev/mmcblk2 bs=256K seek=160 conv=notrunc
    dd if=decrypted.dtb of=/dev/mmcblk2 bs=256K seek=161 conv=notrunc
    sync
    ```
5. Check your stock partitions using `./ampart-v1.4-aarch64-static /dev/mmcblk2 --mode esnapshot`
6. Restore the following snapshot using 
    ```
    ./ampart-v1.4-aarch64-static /dev/mmcblk2 --mode eclone bootloader:0B:4M:0 reserved:36M:64M:0 cache:108M:0B:0 env:116M:8M:0 fip_a:132M:4M:0 fip_b:144M:4M:0 data:156M:-1:4
    ```
7. Use parted to create new MBR partition tables.
    ```sh
    parted
    > unit MiB          # use sector as unit (easy to check)
    > print             # check if the mmc shows
    > mktable msdos     # create new mbr table
    > mkpart primary fat32 4MiB 36MiB       # Use the empty section as /boot
    > mkpart primary ext4 156MiB 3727MiB    # Change the end accordingly
    ```
8. Restore bootloader using
    ```
    dd if=bootloader.img of=/dev/mmcblk2 conv=fsync,notrunc bs=1 count=444
    dd if=bootloader.img of=/dev/mmcblk2 conv=fsync,notrunc bs=512 skip=1 seek=1
    ```
9. Format the partitions and mount the boot partition
    ```
    mkfs.fat -F 16 /dev/mmcblk2p1
    mkfs.ext4 /dev/mmcblk2p2 
    ```
10. reboot into `burn_mode`.
11. Restore rootfs using `python amlogic_devices.py -r 319488 rootfs.ext2`. You may also use nfs and `dd` to do it within the initrd system.
12. Reboot into uInitrd, check the partitions, copy the Image, dtb and `bootargs.txt`(`env/env_p2.txt`, which is for loading bootargs dynamically) to the boot partition.
    ```
    resize2fs /dev/mmcblk2p2
    e2fsck /dev/mmcblk2p2
    mkdir /root/mntpoint
    mount /dev/mmcblk2p1 /root/mntpoint
    scp user@172.16.42.1:/home/user/Image /root/mntpoint
    scp user@172.16.42.1:/home/user/superbird.dtb /root/mntpoint
    ```

# u-boot

OK, now I have the second rabbit hole here (partitioning being the first).

`fatload` and then `go` using a Radxa Zero mainline u-boot bin file actually works. \
This makes Mainline Linux Kernel working, but without any noticable advantages. 

Please check `envs/env_mainline_uboot.txt` for some mainline u-boot environments for booting the same thing as using `envs/env_full_custom.txt` on stock u-boot.

If anyone wants to do something using Mainline u-boot. You can simply build one using Radxa Zero `defconfig`. \
Hopefully this helps.

# Armbian

I took the radxa zero rootfs and successfully boot into Armbian.

By the way, you can not directly write the image to rootfs, the Armbian image is a disk image, not a partition dump. you need to mount the image (`sudo losetup -P /dev/loopX Armbian.img`) and create a partition image (`dd if=/dev/loopXp1 of=armbian_part.img bs=4M status=progress`) to write into your device. \
After that, you need to boot with initrd, copy /lib/modules/x.x.xx to armbian root.

Finally, it needs to have some tweaks before first boot. I disable first time login (`rm /root/.not_logged_in_yet`) and modify the default sshd_config (check `rootfs_overlay/etc/ssh/sshd_config`). 

## g_ether
Add `modules-load=g_ether` to `bootargs.txt` \
Modify `/etc/netplan/armbian-default.yaml` in rootfs.
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

After you log into root, `touch /root/.not_logged_in_yet` and `/usr/lib/armbian/armbian-firstlogin` to run first time login script. \
Essentially, since this is not built for superbird, you should expect that not everything works out of the box (GLES for example), but they do on Buildroot. 
As long as it can be boot into the system, I won't go into all the details from there. Buildroot will still be my focus. 

# Buildroot

https://buildroot.org/ \
[How to clean only target in buildroot](https://stackoverflow.com/questions/47320800/how-to-clean-only-target-in-buildroot)

If I remember correctly, the lack of latest browser and Python in the stock Buildroot is the main reason I started this, LOL ;)

All Buildroot in this repo has root password: `buildroot`. 

There might be a lot of dependencies required by different package, google them should give you some clue.

I select custom kernel inside buildroot only to generate `/lib/modules`.

`cage` is usable. `/root/wlr-randr` is for display transformation etc.

`cog -O renderer=gles` should work with display & touchscreen. 

[Cog Docs](https://igalia.github.io/cog/platform-drm.html#parameters): not the best docs but works.

For touch screen, please check `rootfs_overlay/etc/udev/rules.d/99-tlsc6x-calibration.rules`. \
[libinput transformation](https://wiki.archlinux.org/title/libinput#Via_Udev_Rule)

# Kernel / Device Tree Tweaks

Please check the commits in the kernel repo. 

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

- Accel Sensor: https://www.kernel.org/doc/Documentation/devicetree/bindings/iio/st%2Cst-sensors.yaml
- ALS Sensor: https://www.kernel.org/doc/Documentation/devicetree/bindings/iio/light/tsl2772.txt

Looks like `st,lis2dh12-accel` is not working. I remember it's not in stock firmware as well, so this sensor may not be there after all.

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

# Testing

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

## Auto Brightness with ALS

Please check `rootfs_overlay/root/bl_als.sh`
Ref: https://github.com/AquaUseful/bash-autobrightness/blob/master/auto_br.sh

## Memory Consumption

Normally this current kernel will consume a lot of memory after boot. Setting `swiotlb=512` in bootargs reduced Software IO TLB to 1MB, which will leave you ~450MB memory. There might be other ways, I haven't found any.

## Bluetooth

Please check `rootfs_overlay/root/bt.sh`

Bluetooth Audio: https://github.com/arkq/bluez-alsa \
Bluetooth PAN: https://neonexxa.medium.com/how-to-serve-localhost-in-rapsbery-pi-thru-bluetooth-8e2e0d74da74

## Audio In

Please check `rootfs_overlay/root/amixer.sh`

TODDR IN is fixed. PDM is 4. Use the below command to change the default.

`amixer cset name='TODDR_A SRC SEL' 'IN 4'`

Recording is working, post-processing might be needed. 

`arecord -vvv --device=hw:0,0 --channels=4 --format=S32_LE --rate=48000 --duration=5 --vumeter=mono --file-type=wav test.wav`

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
