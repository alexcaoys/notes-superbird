if [ $(df -m /dev/mmcblk2p2  | tail -1 | awk '{print $4}') -lt 513 ]
then
    echo 'Not enough space for swapfile'
    exit 1
fi
dd if=/dev/zero of=/swapfile bs=1M count=512
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile	swap		swap	defaults	0	0' >> /etc/fstab
echo '/dev/mmcblk2p1	/boot		vfat	defaults,ro	0	2' >> /etc/fstab

mv /root/init_scripts/* /etc/init.d/

rm -r /root/init_scripts
