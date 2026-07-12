# Alpine
Alpine Linux has a really easy setup and extensive packages, including sway, Chromium, etc. And it doesn't have the heavy overhead Debian/Ubuntu has.

## Installation
After you've repartitioned and flashed mainline u-boot, follow the following steps to install Alpine:

1. Download the official U-boot arm64 Image from [here](https://alpinelinux.org/downloads/), you can also download it directly to eMMC inside initramfs thru SSH + g_ether.

2. Untar and copy everything to the partition.
    ```sh
    sudo mount /dev/sda1 /mnt/usbdrive
    cd /mnt/usbdrive
    sudo tar -xf $HOME/downloads/alpine-uboot-x.yy.z-aarch64.tar.gz
    ```
3. Replace kernel + initramfs using the kernel and initramfs you built yourself. Please check [RECOVERY.md](recovery/RECIVERY.md) for kernel and initramfs building. If you don't have ARM64 machine, you just need to replace `/lib/modules` folder in the alpine provided initramfs.

4. Edit `extlinux/extlinux.conf`, change FDTDIR to FDT and modify bootargs:
    ```
    FDT /boot/dtbs-lts/amlogic/meson-g12a-superbird.dtb
    APPEND modules=loop,squashfs,sd-mod,usb-storage,g_ether ip=172.16.42.2::172.16.42.1:255.255.255.0::usb0:::8.8.8.8::
    ```

5. Reboot the device, hopefully everything works. It might take several tries. If it's not working, you can modify the rootfs using USB Mass Storage.

6. Once it's boot, you can follow this general instruction to install it on eMMC. Networking needed.
    ```sh
    setup-alpine # Might need to run more times due to SSL need up to date datetime

    # Unmount as needed
    umount /media/mmcblk1p1
    # Format the sd card
    apk add e2fsprogs
    mkfs.ext4 /dev/mmcblk1p1

    mount /dev/mmcblk1p1 /mnt
    setup-disk -m sys /mnt

    # We might need to use the same kernel + initramfs from before and modify the extlinux file/location.
    ```
    Hopefully we should be able to boot into system now. 

7. After you are inside the system on eMMC, you can `apk add YOUR_KERNEL_PKG` then.

Guide from Alpine: 
- https://wiki.alpinelinux.org/wiki/Alpine_on_ARM
- https://wiki.alpinelinux.org/wiki/Initramfs_init
- setup-alpine: https://wiki.alpinelinux.org/wiki/Installation#Installation_Step_Details
- setup-disk: https://wiki.alpinelinux.org/wiki/System_Disk_Mode

## Usage

Some of the scripts from Buildroot is still useful, please take a look at that folder.

### g_ether
USB Gadget Ethernet (`g_ether`) + IP assignment is configured automatically on Apline initramfs if set the bootargs correctly. \
You can `ssh root@172.16.42.2` after [setting up the host ip](https://wiki.postmarketos.org/wiki/USB_Internet) properly. Here's a handy script for host:
```sh
# INTERFACE might be different for you
INTERFACE=enu1

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

# Armbian
Note: This is some old docs, but the general ideas are the same.

I took the radxa zero rootfs and successfully boot into Armbian.

By the way, you can not directly write the image to rootfs, the Armbian image is a disk image, not a partition dump. you need to mount the image (`sudo losetup -P /dev/loopX Armbian.img`) and create a partition image (`dd if=/dev/loopXp1 of=armbian_part.img bs=4M status=progress`) to write into your device. \
After that, you need to boot with initrd, copy /lib/modules/x.x.xx to armbian root.

Finally, it needs to have some tweaks before first boot. I disable first time login (`rm /root/.not_logged_in_yet`) and modify the default sshd_config to enable root login (same as Buildroot). 

After you log into root, `touch /root/.not_logged_in_yet` and `/usr/lib/armbian/armbian-firstlogin` to run first time login script.

## g_ether
**You'll still need the host configs above.** \
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
