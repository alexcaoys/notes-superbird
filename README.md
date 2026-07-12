# Intro

> [!NOTE]
> Jul. 2026: I'm revisiting this to free up some space. The current goal is to minimize risk and make the implementation as close to mainline as possible.

**superbird** (Spotify Car Thing) should and could be a brilliant device with a compact package, good enough I/O and a soc better than Raspberry Pi 2 W (although without WiFi and ports). Please keep in mind that this is an embedded device, don't expect it to solve any complicated tasks! 

Anyway, if you still think this will become e-waste for you, **you can for sure support this project by sending it to me :)**

> [!CAUTION]
> TRY EVERYTHING BELOW AT YOUR OWN RISK!!! If you don't know what you are doing, STOP. 

If you need the old information regarding stock u-boot + Linux 6.6 + Buildroot, please check the `stock-uboot` branch.

For notes on my kernel tweaks as well as support matrix, please refer to [`BUILDING.md`](BUILDING.md).

# Release

There will be no "release" in the future, this is pretty much the final stage.

Bootloader based on mainline u-boot. \
Kernel based on mainline Linux. \
System (could be) based on Alpine Linux. (Others should be possible as well.)

# TL;DR

**Beaware of all the consequences and you can get started.**

The old way always work with the stock u-boot. \
But as many information points out, Meson G12A can actually directly boot a u-boot from USB (ie. `boot-g12a.py` from [pyamlboot](https://github.com/superna9999/pyamlboot/tree/master)). \
From the information found [here](https://github.com/ThingLabsOSS/superbird-fip-tools/tree/main), there is only one encrypt key away, and it was provided by Spotify [here](https://github.com/spsgsb/uboot/blob/buildroot-openlinux-201904-g12a/board/amlogic/superbird_production/aml-user-key.sig).

Combining these two and we can get a decent recovery mode. I wrote a small script to boot the device directly. All the necessary files are in `recovery` and build steps is in [`RECOVERY.md`](recovery/RECOVERY.md).

## USB Mass Storage
```sh
python -m pip install git+https://github.com/superna9999/pyamlboot
# If `pyusb` give you access denied etc., please check https://github.com/pyusb/pyusb/issues/237
cd recovery
# Hold Button 1+4 and plug into USB. 

# Mount eMMC as USB Mass Storage (/dev/sdx)
python ./g12a_boot.py \
    ./emmc.encrypt.bin \
    --bl2 ./stock.bootloader.bin
```
Now you should be able to see a USB Drive which is your on-board eMMC, you can directly write the u-boot the same way below. Maybe we should wipe the eMMC once here. If it doesn't work somehow, try **Linux Recovery**, you might need to repartition the eMMC first. 

## Linux Recovery
```sh
python ./g12a_boot.py \
    ./u-boot.encrypt.bin \
    --fitimage ./g12a.itb \
    --bl2 ./stock.bootloader.bin
```
You might need to try again a few times since the USB DFU is not the most stable thing in the world.

Since the display is fully functional now, once you can see logs popping up, you should be able to `ssh` into it. On Linux (`enu1` is what I have, you might have something else):
```sh
sudo ip address add dev enu1 172.16.42.1/24
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@172.16.42.2
```

## Install something else

It's perfectly safe to wipe everything on eMMC since the recovery doesn't rely on eMMC. Everything below is using the Linux recovery, but should work with the USB Mass Storage as well.

1. Use parted to create new MBR partition tables.
    ```sh
    parted /dev/mmcblk1
    > unit MiB          # use sector as unit (easy to check)
    > print             # check if the mmc shows
    > mktable msdos     # create new mbr table
    > mkpart primary ext4 4MiB -1    # Keep the first 4MiB for bootloader
    > set 1 boot on
    mkfs.ext4 /dev/mmcblk1p1
    ```
2. Transfer the encrypted bootloaders to eMMC, on your host
    ```sh
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ./u-boot.encrypt.bin.sd.bin root@172.16.42.2:
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ./stock.bootloader.bin root@172.16.42.2:
    ```
3. Restore bootloader using
    ```sh
    dd if=./u-boot.encrypt.bin.sd.bin of=/dev/mmcblk1 conv=fsync,notrunc bs=512 skip=1 seek=1
    # BL2 still needs stock
    dd if=./stock.bootloader.bin of=/dev/mmcblk1 conv=fsync,notrunc bs=512 skip=1 seek=1 count=127
    dd if=./stock.bootloader.bin of=/dev/mmcblk1 conv=fsync,notrunc bs=1 count=440
    ```
4. And then you can do whatever you want using the eMMC, as long as it's compatible with Mainline u-boot. And you'll need some kernel patches here. I'll put my general Alpine steps in [ALPINE.md](ALPINE.md).
