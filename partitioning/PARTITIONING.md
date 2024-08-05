
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
12. Reboot into uInitrd, check the partitions, copy the Image, dtb and `bootargs.txt`(`uboot_envs/env_p2.txt`), which is for loading bootargs dynamically to the boot partition.
    ```
    /root/init_resize2fs.sh
    mount /dev/mmcblk2p1 /boot
    scp user@172.16.42.1:/home/user/Image /boot
    scp user@172.16.42.1:/home/user/superbird.dtb /boot
    scp user@172.16.42.1:/home/user/env_p2.txt /boot/bootargs.txt
    ```
