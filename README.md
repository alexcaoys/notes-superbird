# Intro

**superbird** (Spotify Car Thing) should and could be a brilliant device with a compact package, good enough I/O and a soc better than Raspberry Pi 2 W (although without WiFi and ports). Please keep in mind that this is an embedded device, don't expect it to solve any complicated tasks!

Anyway, if you still think this will become e-waste for you, **you can for sure support this project by sending it to me :)**

**TRY EVERYTHING BELOW AT YOUR OWN RISK!!!**

**EXPERT USERS ONLY. If you don't know what you are doing, STOP**.

**Kernel repo**: https://github.com/alexcaoys/linux-superbird-6.6.y

For notes on my kernel tweaks as well as support matrix, please refer to [BUILDING.md](https://github.com/alexcaoys/notes-superbird/blob/main/BUILDING.md).

## Release

**Please Check [RELEASE_NOTES.md](https://github.com/alexcaoys/notes-superbird/blob/main/RELEASE_NOTES.md) for details.**

Compiled Kernel will be available on Kernel Repo [release](https://github.com/alexcaoys/linux-superbird-6.6.y/releases) section.

Since display is only working partially, I don't consider this as good for all users. But you are welcome to try. Hopefully we can get this fix ASAP.

I will consider uploading my Buildroot rootfs to this release page. But Buildroot is pretty much a customizable system so do try it out on your own. **It's amazing!**

# Boot

- pyamlboot: https://github.com/superna9999/pyamlboot (For `pyusb` to work, [please check](https://github.com/pyusb/pyusb/issues/237))
- Restore partitions using superbird-tool: 
  - https://github.com/Car-Thing-Hax-Community/superbird-tool
  - https://github.com/bishopdynamics/superbird-tool ([maintainer seems MIA, not updating](https://github.com/alexcaoys/notes-superbird/issues/6))
- kernel params: https://www.kernel.org/doc/html/v6.6/admin-guide/kernel-parameters.html

**In order for the display color to work properly, we need to bypass `init_display` within u-boot, you can either **

- restore `uboot_envs/env_full_dualboot.txt` using superbird-tool `--send_full_env` feature, or

- enter from USB mode and then enter superbird-tool `--burn_mode`

Thanks @Fexiven for noticing this ([our discussion here](https://github.com/alexcaoys/notes-superbird/issues/3)).

I took parts from `superbird-tool` and wrote the script for booting custom stuff: Please check `amlogic_device.py`.

## Boot using initrd

**All in one** tar is available on Release page now.

I created an Buildroot uInitrd image in case anything need an in-RAM system (repartitioning for example), please find it in Release and use `initrd/env_initrd.txt` in this repo to boot. **You will need this often when you are working to build an embedded system (ie. Buildroot)**

Please use `python amlogic_device.py -i ENV_FILE KERNEL_FILE INITRD_FILE DTB_FILE` to boot kernel + dtb + uInitrd from host. Please check `initrd` folder.

## Boot into stock partitions

set `active_slot=_b` and **clear dtbo_b partition**. Otherwise custom dtb won't be loaded.

1. Create empty `dtbo_b` and `boot_b` partitions by `dd` and restore to device.
2. Restore new buildroot partition to `system_b`.
3. Use `uboot_envs/env_b.txt` in this repo to boot. (`python amlogic_device.py -c ENV_FILE KERNEL_FILE DTB_FILE` to boot kernel + dtb from host)

## Boot into custom partitions

After **repartitioning** and restoring the rootfs as the below section. 

Use `uboot_envs/env_p2.txt` in this repo to boot. 

- `python amlogic_device.py -c ENV_FILE KERNEL_FILE DTB_FILE` to boot kernel + dtb from host, **OR**
- Using `fatload` to load kernel and dtb from `mmcblk2p1` and `python amlogic_device.py -m ENV_FILE` to boot. **OR**
- Send `env/env_full_custom.txt` to the device. Button 4 for burn mode, Normally it will load envs from `bootargs.txt` within `mmcblk2p1` and then boot into `mmcblk2p2` using `Image` and `superbird.dtb` from `mmcblk2p1`.

# Partitioning

Allow the unifreq kernel to read AML partition table: https://github.com/ophub/amlogic-s9xxx-armbian/issues/1109

## Repartitioning

- AML Partition Tables: https://7ji.github.io/embedded/2022/11/11/ept-with-ampart.html
- Decrypt AML dtb: https://7ji.github.io/crack/2023/01/08/decrypt-aml-dtb.html
- ampart Tool: https://github.com/7Ji/ampart/tree/master

**Remember to backup**

[full reserved partition backup](https://github.com/err4o4/spotify-car-thing-reverse-engineering/issues/30#issuecomment-2161567419) \
My backup `ampart` partitions output is in `ampart_partitions.txt`.

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
12. Reboot into uInitrd, check the partitions, copy the Image, dtb and `bootargs.txt`(`uboot_envs/env_p2.txt`), which is for loading bootargs dynamically) to the boot partition.
    ```
    resize2fs /dev/mmcblk2p2
    e2fsck /dev/mmcblk2p2
    mkdir /root/mntpoint
    mount /dev/mmcblk2p1 /root/mntpoint
    scp user@172.16.42.1:/home/user/Image /root/mntpoint
    scp user@172.16.42.1:/home/user/superbird.dtb /root/mntpoint
    ```

# Buildroot

https://buildroot.org/ \
[How to clean only target in buildroot](https://stackoverflow.com/questions/47320800/how-to-clean-only-target-in-buildroot)

If I remember correctly, the lack of latest browser and Python in the stock Buildroot is the main reason I started this, LOL ;)

All Buildroot in this repo has root password: `buildroot`. \
There might be a lot of dependencies required by different package, google them should give you some clue. \
I select custom kernel inside buildroot only to generate `/lib/modules`.

`sway` is a really great base here (ie. `i3` on `wayland`). All the output transformation, input mapping can all be done with `sway`. To use it without `systemd`, I implemented [this W.I.P. patch](
https://lore.kernel.org/buildroot/?q=package%2Fsway:+make+systemd+optional&x=t) for Buildroot. \
`cog` Browser could work on it. autologin + autolaunch `sway` is already here. I will put my `config` here after I've done testing.

Standalone `cog -O renderer=gles` should also work with display & touchscreen. [Cog Docs](https://igalia.github.io/cog/platform-drm.html): not the best docs but works. For touch screen, please check [libinput transformation](https://wiki.archlinux.org/title/libinput#Via_Udev_Rule)

**I put some probably essential commands in `first_login.sh`, please take a look. (which including copying some `init.d` scripts from `/root` to `/etc/init.d`)**

## g_ether
USB Gadget Ethernet (`g_ether`) is enabled automatically (Please check `buildroot/rootfs_overlay/etc/init.d/S49gether`) on Buildroot so you can `ssh root@172.16.42.2` after [setting up the host ip](https://wiki.postmarketos.org/wiki/USB_Internet) properly. Here's a handy script:
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

## USB Host
Drivers included after `6.6.37_20240706`. I only included USB Ethernet and Mass Storage Drivers, please let me know if others are needed. \
USB Host mode is working (although persumably only USB 2.0 speed). 

`echo host > /sys/class/usb_role/ffe09000.usb-role-switch/role`

For Ethernet Adapter, please check `buildroot/rootfs_overlay/root/init_scripts/S40network`. \
If you set `network=eth` in bootargs, it will try to bring up usb host ethernet adapter first before fallback back to g_ether. It is not guarenteed to work under all circumstances.

## Memory Consumption / swap

Normally this kernel will consume a lot of memory after boot. Setting `swiotlb=512` in bootargs reduced Software IO TLB to 1MB, which will leave you ~450MB memory. There might be other ways, I haven't found any.

Please check `buildroot/rootfs_overlay/root/first_login.sh`, which create 512MB swap `/swapfile` and perform other stuff. \
Creating a swapfile can relief some pressure on memory. (https://linuxize.com/post/create-a-linux-swap-file/)

## Auto Brightness with ALS

Please check `buildroot/rootfs_overlay/root/bl_als.sh`

Ref: https://github.com/AquaUseful/bash-autobrightness/blob/master/auto_br.sh

## Bluetooth

Please check `buildroot/rootfs_overlay/root/bt.sh`

Bluetooth Audio: https://github.com/arkq/bluez-alsa \
Bluetooth PAN: https://neonexxa.medium.com/how-to-serve-localhost-in-rapsbery-pi-thru-bluetooth-8e2e0d74da74

## Audio In

TODDR IN is fixed. PDM is 4. Use the below command to change the default.

`amixer cset name='TODDR_A SRC SEL' 'IN 4'`

I put it in `buildroot/rootfs_overlay/root/init_scripts/S89amixer`

Recording is working, post-processing might be needed. 

`arecord -vvv --device=hw:0,0 --channels=4 --format=S32_LE --rate=48000 --duration=5 --vumeter=mono --file-type=wav test.wav`

# EXTRA

## u-boot

- [Radxa Zero u-boot Docs](https://docs.u-boot.org/en/latest/board/amlogic/radxa-zero.html)

OK, now I have the second rabbit hole here (partitioning being the first).

`fatload` and then `go` using a Radxa Zero mainline u-boot bin file actually works. \
**This makes Mainline Linux Kernel working, but without any noticable advantages.** 

Please check `uboot_envs/env_mainline_uboot.txt` for some mainline u-boot environments for booting the same thing as using `uboot_envs/env_full_custom.txt` on stock u-boot.

If anyone wants to do something using Mainline u-boot. You can simply build one using Radxa Zero `defconfig`. \
Hopefully this helps.

## Armbian

I took the radxa zero rootfs and successfully boot into Armbian.

By the way, you can not directly write the image to rootfs, the Armbian image is a disk image, not a partition dump. you need to mount the image (`sudo losetup -P /dev/loopX Armbian.img`) and create a partition image (`dd if=/dev/loopXp1 of=armbian_part.img bs=4M status=progress`) to write into your device. \
After that, you need to boot with initrd, copy /lib/modules/x.x.xx to armbian root.

Finally, it needs to have some tweaks before first boot. I disable first time login (`rm /root/.not_logged_in_yet`) and modify the default sshd_config (check `rootfs_overlay/etc/ssh/sshd_config`). 

### g_ether
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

After you log into root, `touch /root/.not_logged_in_yet` and `/usr/lib/armbian/armbian-firstlogin` to run first time login script. \
Essentially, since this is not built for superbird, you should expect that not everything works out of the box (GLES for example), but they do on Buildroot. \
As long as it can be boot into the system, I won't go into all the details from there. Buildroot will still be my focus. 

# Reference

## u-Boot
- Stock u-boot: https://github.com/spsgsb/uboot
- Amlogic Boot: https://7ji.github.io/embedded/2022/11/11/amlogic-booting.html
- booti: https://docs.u-boot.org/en/v2021.04/usage/booti.html