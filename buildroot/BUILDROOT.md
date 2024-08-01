
# Buildroot

If I remember correctly, the lack of latest browser and Python in the stock Buildroot is the main reason I started this, LOL ;)

All Buildroot in this repo has root password: `buildroot`. 

**I put some probably essential commands in `first_login.sh`, please take a look.**

I select custom kernel inside buildroot only to generate `/lib/modules`. 

## rootfs_overlay

```sh
rootfs_overlay/
├── boot                    # for Mounting /dev/mmcblk2p1
├── etc
│   ├── bluetooth
│   │   └── main.conf       # change default bluetooth adapter name
│   ├── init.d
│   │   ├── S40network      # USB Host Ethernet Setup
│   │   ├── S48gether       # USB Gadget g_ether Setup
│   │   ├── S49amixer       # setup default PDM microphone
│   │   └── S89bluetooth    # using btattach to bring up UART Bluetooth
│   ├── inittab             # auto login
│   ├── pulse
│   │   └── system.pa       # pulseaudio enable bluetooth for root
│   ├── resolv.conf         # nameserver
│   └── ssh
│       └── sshd_config     # enable ssh root login
├── root
│   ├── .bashrc             # setup bash profile
│   ├── .config
│   │   └── sway
│   │       └── config      # example sway config
│   ├── .local
│   │   └── share
│   │       └── glib-2.0
│   │           └── schemas # overskride gschema file
│   │               ├── gschemas.compiled
│   │               └── io.github.kaii_lb.Overskride.gschema.xml
│   ├── .profile            # sh profile + auto launch sway
│   ├── ampart-v1.4-aarch64-static  # ampart partition tools
│   ├── bl_als.sh           # auto backlight script
│   └── first_login.sh      # first time login script, swap creation etc.
└── usr
    ├── lib
    │   ├── firmware
    │   │   └── brcm        # bluetooth firmware
    │   │       ├── BCM.hcd
    │   │       └── BCM20703A2.hcd
    │   └── gdk-pixbuf-2.0  # rsvg loader for overskride
    │       └── 2.10.0
    │           └── loaders
    │               └── libpixbufloader-svg.so
    └── share
        └── overskride      # gresource for overskride
            └── overskride.gresource

23 directories, 21 files
```

## GUI Applications
### sway
`sway` is a really great base here (ie. `i3` on `wayland`). All the output transformation, input mapping can all be done with `sway`. To use it without `systemd`, I implemented [this W.I.P. patch](
https://lore.kernel.org/buildroot/?q=package%2Fsway:+make+systemd+optional&x=t) for Buildroot. \
autologin + autolaunch `sway` is included. Please check `buildroot/rootfs_overlay/root/.config/sway/config` for some handy sway setup.

### cog
I include `cog` Browser on Buildroot. It can work on `sway`. \
Standalone `cog -O renderer=gles` should also work with display & touchscreen. [Cog Docs](https://igalia.github.io/cog/platform-drm.html): not the best docs but works. For touch screen, please check [libinput transformation](https://wiki.archlinux.org/title/libinput#Via_Udev_Rule).

Test `cog` on `sway`: 
```
export XDG_RUNTIME_DIR=/run
export $(dbus-launch)
export GST_DEBUG=2,autoaudiosink:6,pulse*:6
cog https://www.youtube.com/embed/9bZkp7q19f0`
```

### overskride (Bluetooth)
I added `overskride` to Buildroot so that users can connect to a bluetooth keyboard or speakers easily without keyboard or ssh. But `bluetoothctl` will always be the ultimate solution for bluetooth. Please check bluetooth section below.

Please check `buildroot/package` for added packages (`libgtk4` can be found on buildroot git, also need some tweaks for `librsvg` and `gresource` but I included the built version in `rootfs_overlay`)

Test `overskride` on `sway`: `XDG_RUNTIME_DIR=/run G_MESSAGES_DEBUG=all WAYLAND_DISPLAY=wayland-1 overskride
`

## g_ether
USB Gadget Ethernet (`g_ether`) is enabled automatically (Please check `buildroot/rootfs_overlay/etc/init.d/S49gether`) on Buildroot so you can `ssh root@172.16.42.2` after [setting up the host ip](https://wiki.postmarketos.org/wiki/USB_Internet) properly. Here's a handy script for host:
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

## Memory Consumption / swap

Normally this kernel will consume a lot of memory after boot. Setting `swiotlb=512` in bootargs reduced Software IO TLB to 1MB, which will leave you ~450MB memory. There might be other ways, I haven't found any.

Please check `buildroot/rootfs_overlay/root/first_login.sh`, which create 512MB swap `/swapfile` and perform other stuff.

## Auto Brightness with ALS

Please check `buildroot/rootfs_overlay/root/bl_als.sh`

Ref: https://github.com/AquaUseful/bash-autobrightness/blob/master/auto_br.sh

## Audio In

TODDR IN is fixed. PDM is 4. Use the below command to change the default.

`amixer cset name='TODDR_A SRC SEL' 'IN 4'`

I put it in `buildroot/rootfs_overlay/etc/init.d/S89amixer`

Recording is working, post-processing might be needed. 

`arecord -vvv --device=hw:0,0 --channels=4 --format=S32_LE --rate=48000 --duration=5 --vumeter=mono --file-type=wav test.wav`

## USB Host

USB Host mode is working (although persumably only USB 2.0 speed). Drivers included after `6.6.37_20240706`. I only included USB Ethernet and Mass Storage Drivers, please let me know if others are needed.

`echo host > /sys/class/usb_role/ffe09000.usb-role-switch/role`

For Ethernet Adapter, please check `buildroot/rootfs_overlay/etc/init.d/S40network`. \
If you set `network=eth` in bootargs, it will try to bring up usb host ethernet adapter first before fallback back to g_ether. It is not guarenteed to work under all circumstances.

## Bluetooth

Please check `buildroot/rootfs_overlay/etc/init.d/S89bluetooth`

For PulseAudio to work for `root`, we need to modify `system.pa`, enable module loading, and add root to `pulse-access` group. Please check `buildroot/rootfs_overlay/etc/pulse/system.pa`.

### Some advanced use cases:

1. **Tested**: As phone's bluetooth speaker(bridge). (Essentially **Car Thing without Spotify**. pulseaudio do it for you) \
https://www.cyberciti.biz/mobile-devices/linux-set-up-bluetooth-speaker-to-stream-audio-from-your-android-ios-mobile-phone/ \
By the way, it seems you need to use `bluetoothctl` for this.
2. As other devices bluetooth keyboard/input (?): Something like [this](https://aur.archlinux.org/packages/hidclient) \
3. Bluetooth PAN: https://neonexxa.medium.com/how-to-serve-localhost-in-rapsbery-pi-thru-bluetooth-8e2e0d74da74

## Reference


- https://buildroot.org/
- [How to clean only target in buildroot](https://stackoverflow.com/questions/47320800/how-to-clean-only-target-in-buildroot)
