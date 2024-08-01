# Intro

**superbird** (Spotify Car Thing) should and could be a brilliant device with a compact package, good enough I/O and a soc better than Raspberry Pi 2 W (although without WiFi and ports). Please keep in mind that this is an embedded device, don't expect it to solve any complicated tasks!

Anyway, if you still think this will become e-waste for you, **you can for sure support this project by sending it to me :)**

**TRY EVERYTHING BELOW AT YOUR OWN RISK!!!**

**EXPERT USERS ONLY. If you don't know what you are doing, STOP**.

**Kernel repo**: https://github.com/alexcaoys/linux-superbird-6.6.y

For notes on my kernel tweaks as well as support matrix, please refer to [BUILDING.md](https://github.com/alexcaoys/notes-superbird/blob/main/BUILDING.md).

## Release

**[RELEASE_NOTES.md](https://github.com/alexcaoys/notes-superbird/blob/main/RELEASE_NOTES.md)**

Compiled Kernel will be available on Kernel Repo [release](https://github.com/alexcaoys/linux-superbird-6.6.y/releases) section.

Since display is only working partially, I don't consider this as good for all users. But you are welcome to try. Hopefully we can get this fix ASAP.

I will consider uploading my Buildroot rootfs to this release page. But Buildroot is pretty much a customizable system so do try it out on your own. **It's amazing!**

# Boot

- pyamlboot: https://github.com/superna9999/pyamlboot (For `pyusb` to work, [please check](https://github.com/pyusb/pyusb/issues/237))
- Restore partitions using superbird-tool: 
  - https://github.com/Car-Thing-Hax-Community/superbird-tool
  - https://github.com/bishopdynamics/superbird-tool ([maintainer seems MIA, not updating](https://github.com/alexcaoys/notes-superbird/issues/6))
- kernel params: https://www.kernel.org/doc/html/v6.6/admin-guide/kernel-parameters.html

**In order for the display color to work properly, we need to bypass `init_display` within u-boot, you can either**

- restore `uboot_envs/env_full_dualboot.txt` using superbird-tool `--send_full_env` feature, or

- enter from USB mode and then enter superbird-tool `--burn_mode`

Thanks @Fexiven for noticing this ([our discussion here](https://github.com/alexcaoys/notes-superbird/issues/3)).

I took parts from `superbird-tool` and wrote the script for booting custom stuff: Please check `amlogic_device.py`.

## Boot using initrd

**All in one** tarball is [available](https://github.com/alexcaoys/notes-superbird/releases/tag/20240724) on Release page. `cd` into the folder and `./initrd.sh` to boot into initrd.

I created an Buildroot uInitrd image in case anything need an in-RAM system (repartitioning for example), please find it in Release and use `initrd/env_initrd.txt` in this repo to boot. **You will need this often when you are working to build an embedded system (ie. Buildroot)**

Please use `python amlogic_device.py -i ENV_FILE KERNEL_FILE INITRD_FILE DTB_FILE` to boot kernel + dtb + uInitrd from host. Please check `initrd` folder.

## Boot into stock partitions

set `active_slot=_b` and **clear dtbo_b partition**. Otherwise custom dtb won't be loaded.

1. Create empty `dtbo_b` and `boot_b` partitions by `dd` and restore to device.
2. Restore new buildroot partition to `system_b`.
3. Use `uboot_envs/env_b.txt` in this repo to boot. (`python amlogic_device.py -c ENV_FILE KERNEL_FILE DTB_FILE` to boot kernel + dtb from host)

## Boot into custom partitions

After **repartitioning** and restoring the rootfs as [`PARTITIONING.md`](https://github.com/alexcaoys/notes-superbird/blob/main/partitioning/PARTITIONING.md).

Use `uboot_envs/env_p2.txt` in this repo to boot. 

- `python amlogic_device.py -c ENV_FILE KERNEL_FILE DTB_FILE` to boot kernel + dtb from host, **OR**
- Using `fatload` to load kernel and dtb from `mmcblk2p1` and `python amlogic_device.py -m ENV_FILE` to boot. **OR**
- Send `env/env_full_custom.txt` to the device. Button 4 for burn mode, Normally it will load envs from `bootargs.txt` within `mmcblk2p1` and then boot into `mmcblk2p2` using `Image` and `superbird.dtb` from `mmcblk2p1`.

# Partitioning
[`PARTITIONING.md`](https://github.com/alexcaoys/notes-superbird/blob/main/partitioning/PARTITIONING.md)

# Buildroot

[`BUILDROOT.md`](https://github.com/alexcaoys/notes-superbird/blob/main/buildroot/BUILDROOT.md)

# EXTRA

- [u-Boot](https://github.com/alexcaoys/notes-superbird/blob/main/BUILDING.md#u-boot)
- [Armbian](https://github.com/alexcaoys/notes-superbird/blob/main/BUILDING.md#armbian)