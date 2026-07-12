
# Buildroot
**This is something legacy, so I removed a lot of things. but others are still salvageable.**

If I remember correctly, the lack of latest browser and Python in the stock Buildroot is the main reason I started this, LOL ;)

All Buildroot in this repo has root password: `buildroot`. 

I select custom kernel inside buildroot only to generate `/lib/modules`. 

## rootfs_overlay

```sh
rootfs_overlay/
├── etc
│   ├── bluetooth
│   │   └── main.conf       # change default bluetooth adapter name
│   ├── init.d
│   │   ├── S40network      # USB Host Ethernet Setup
│   │   ├── S48gether       # USB Gadget g_ether Setup
│   │   ├── S49amixer       # setup default PDM microphone
│   ├── pulse
│   │   ├── daemon.conf     # define default configs for microphone
│   │   └── system.pa       # pulseaudio enable bluetooth for root
├── root
│   ├── .config
│   │   └── sway
│   │       └── config      # example sway config
│   ├── bl_als.sh           # auto backlight script
└── usr
    ├── lib
    │   ├── firmware
    │   │   └── brcm        # bluetooth firmware
    │   │       ├── BCM.hcd
    │   │       └── BCM20703A2.hcd
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
