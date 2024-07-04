# mount /dev/mmcblk2p1 /boot
resize2fs /dev/mmcblk2p2
e2fsck /dev/mmcblk2p2
