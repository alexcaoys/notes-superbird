# Building Recovery

## Mainline U-Boot for superbird
**Building mainline U-Boot for the Superbird is essentially the same as building it for the Radxa Zero**: https://docs.u-boot.org/en/stable/board/amlogic/radxa-zero.html

The only additional step is image encryption. The required process is already implemented in Claude's scripts, specifically [here](https://github.com/ThingLabsOSS/superbird-fip-tools/blob/main/python/fip-rebuild.sh#L110-L115). We just need the encryption key provided by Spotify [here](https://github.com/spsgsb/uboot/blob/buildroot-openlinux-201904-g12a/board/amlogic/superbird_production/aml-user-key.sig).

`aml_encrypt_g12a` is only available as an x86_64 binary, but this is not a problem since the LibreELEC project runs it through `qemu-x86_64`. After building U-Boot for the Radxa Zero, simply run:
```sh
qemu-x86_64 ./radxa-zero/aml_encrypt_g12a --bootsig \
    --input  "my-output-dir/u-boot.bin" \
    --amluserkey ../aml-user-key.sig \
    --aeskey enable \
    --output "my-output-dir/u-boot.encrypt.bin" \
    --level 3
```

Generating the encrypted image is only part of the process. Booting the encrypted image directly still results in boot failures (I haven't checked the UART output, so I'm not sure what the exact error is). However, based on Claude's implementation [here](https://github.com/ThingLabsOSS/superbird-fip-tools/blob/main/python/flash_boot_partition.py#L101-L111), the issue can be worked around by preserving the first 64 KiB from the stock U-Boot.

Coincidentally, this is also the first region that `pyamlboot` writes to the device (there is likely a deeper explanation for why this works). In practice, the solution is to combine the first 64 KiB of the stock bootloader with the remainder of the newly built encrypted U-Boot images. The same approach should be used when flashing to eMMC. This is why the `pyamlboot` and `dd` commands in this repository differ from the standard U-Boot documenetation.

By the way, setting up the build environment is straightforward using an Alpine Linux Docker image:
```sh
# Put u-boot source code and amlogic-boot-fip in ./u-boot, and then
docker run -it --rm -v ./u-boot:/home/buildozer/u-boot alpinelinux/build-base:latest /bin/sh

echo -e "http://dl-cdn.alpinelinux.org/alpine/edge/community" | doas -u root tee -a /etc/apk/repositories
doas apk add alpine-sdk bc bison dtc flex gnutls-dev linux-headers ncurses-dev openssl-dev perl py3-elftools py3-setuptools python3-dev swig util-linux-dev

# For FIP
doas apk add qemu-x86_64 bash
# Follow the above guide afterward.
```

## U-Boot environment setup
For both USB Mass Storage u-boot and general u-boot, the only change on top of radxa-zero is the environment variable. \
Just need to put the override environment files in `board/amlogic/u200` and set `CONFIG_ENV_SOURCE_FILE`. \
But since for `meson64`, `CFG_EXTRA_ENV_SETTINGS` still takes priority, we need to modify that logic. Apply this patch in u-boot source tree.
```sh
git apply u-boot-env-default.patch
```

The eMMC USB Mass Storage environment is in `emmc_ums.env` \
The DFU Linux Recovery environment is in `dfu_recovery.env`

DFU: https://docs.u-boot.org/en/stable/usage/dfu.html

## Alpine initramfs setup
Build environment can be the same as the u-boot one, it's also pretty easy to build Alpine apks using this image. For example, build your own kernel apk. **Kernel package should be able to be cross compiled. You might need an ARM64 docker to build initramfs.** \
Patch and build your kernel image like this: https://gitlab.alpinelinux.org/alpine/aports/-/blob/master/main/linux-lts/APKBUILD
```sh
doas apk add KERNEL_PKG

doas apk add dropbear e2fsprogs mkinitfs parted openssh-sftp-server
```
Add/edit the following files:
```sh
# /etc/mkinitfs/features.d/gadget.modules
kernel/drivers/usb/gadget

# /etc/mkinitfs/features.d/dropbear.files
/usr/sbin/dropbear
/usr/bin/dropbearkey
/usr/lib/ssh/*

# /etc/mkinitfs/features.d/ext4.files
/sbin/e2fsck
/sbin/fsck.ext4
/sbin/mke2fs
/sbin/mkfs.ext4

# /etc/mkinitfs/features.d/parted.files
/usr/lib/libparted*
/usr/sbin/parted
/usr/sbin/partprobe

# /etc/mkinitfs/mkinitfs.conf 
features="base dropbear ext4 gadget keymap kms mmc network parted usb phy"
```

Modify this template https://github.com/alpinelinux/mkinitfs/blob/master/initramfs-init.in
```sh
# dropbear for recovery
# before Entering single mode, add dropbear to myopts
if [ "$KOPT_dropbear" = "yes" ]; then
    passwd -d root
    mkdir /etc/dropbear

    if [ ! -e /etc/dropbear/dropbear_rsa_host_key ] ; then
        echo "Generating RSA-Hostkey..."
        /usr/bin/dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key
    fi
    if [ ! -e /etc/dropbear/dropbear_ecdsa_host_key ] ; then
        echo "Generating ECDSA-Hostkey..."
        /usr/bin/dropbearkey -t ecdsa -f /etc/dropbear/dropbear_ecdsa_host_key
    fi
    if [ ! -e /etc/dropbear/dropbear_ed25519_host_key ] ; then
        echo "Generating ED25519-Hostkey..."
        /usr/bin/dropbearkey -t ed25519 -f /etc/dropbear/dropbear_ed25519_host_key
    fi

    ebegin "Starting dropbear"
    /usr/sbin/dropbear -B
fi
```
Build the `initramfs`:
```sh
doas mkinitfs -i ./init $(ls /lib/modules)
```

## Optional: FIT Image
As you can see in the Python script, you can use kernel+dtb+initramfs or a single FIT image to boot. Please refer to U-Boot documentation: https://docs.u-boot.org/en/stable/usage/fit/howto.html

## u-Boot
- Stock u-boot: https://github.com/spsgsb/uboot
