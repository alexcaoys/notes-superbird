# Release Note

## Latest

- Buildroot: [buildroot_20240804](https://github.com/alexcaoys/notes-superbird/releases/tag/20240804)

    First release of Buildroot. Please check `README.md` for details.

    - Using `initrd/config_buildroot_sway_overskride`. 
    - Based on Buildroot 2024.02.4, but there are some tweaks (Sway + Overskride).
    - Both `g_ether` and USB `eth` is available, please read `BUILDROOT.md` for details.
    - Sway key mapping, Bluetooth, Browser examples included. 

- Linux & modules: [6.6.43_20240801](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.43_20240801)

    Using `config_linux_20240729`.

    Sync Kernel with upstream to 6.6.43.
    Add UHID Support for Bluetooth Inputs.

    Working `panel-sitronix-st7701.c` config: The same as 6.6.32_20240618 below.

- uInitrd: [initrd_20240724](https://github.com/alexcaoys/notes-superbird/releases/tag/20240724)

    Since this should contain all the features needed for **repartitioning and rescue rootfs**, in the future there won't be regular release of initrd. This release will be **all in one**, you still need to install `pyamlboot`, and then, `bash initrd.sh` should help you enter the initramfs.

    - Remove unnecessary stuff, downsize the image to ~40MB.
    - Using `initrd/config_buildroot_initrd`. 
    - `ampart` included in `/root`
    - `g_ether` will be enabled at boot. `ssh` is available. 
    - For partitioning only.

## Kernel

- Linux: [6.6.41_20240724](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.41_20240724)

    Using `config_linux_20240724`.

    Sync Kernel with upstream to 6.6.41.

    Working `panel-sitronix-st7701.c` config: The same as 6.6.32_20240618 below.

- Linux: [6.6.37_20240706](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.37_20240706)

    Using `config_linux_20240702`.

    Sync Kernel with upstream to 6.6.37. 
    Remove accel sensor from dts.
    Add USB host drivers (mass storage and ethernet).

    Working `panel-sitronix-st7701.c` config: The same as 6.6.32_20240618 below.

- Linux: [6.6.35_20240622](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.35_20240622)

    Using `config_linux_20240622`.

    Sync Kernel with upstream to 6.6.35. 

    Working `panel-sitronix-st7701.c` config: The same as 6.6.32_20240618 below.

- Linux: [6.6.32_20240618](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.32_20240618)

    Using `config_linux_20240616`.

    Add and remove some features/drivers from the kernel and integrate most of thing into the kernel (keep number of modules as less as possible)

    Working `panel-sitronix-st7701.c` config:
    ```
	.clock          = 36000,

	.hdisplay       = 480,
	.hsync_start    = 480 + 20, 
	.hsync_end      = 480 + 20 + 120,
	.htotal         = 480 + 20 + 120 + 20,

	.vdisplay       = 800,
	.vsync_start    = 800 + 2,
	.vsync_end      = 800 + 2 + 840,
	.vtotal         = 800 + 2 + 840 + 10,
    ```
    and dts config:
    ```
    CLKID_GP0_PLL = CLKID_MIPI_DSI_PXCLK = 432000000
    ```

- Linux: [6.6.32_20240610](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.32_20240610)

    First release. Using `config_linux_20240610`. This image doesn't have the working panel config. So the display won't have the correct color.

    But here is a working `panel-sitronix-st7701.c` config:
    ```
    .clock          = 36000,

	.hdisplay       = 480,
	.hsync_start    = 480 + 32,
	.hsync_end      = 480 + 32 + 120,
	.htotal         = 480 + 32 + 120 + 32,

	.vdisplay       = 800,
	.vsync_start    = 800 + 16,
	.vsync_end      = 800 + 16 + 640,
	.vtotal         = 800 + 16 + 640 + 16,
    ```
    and dts config:
    ```
    CLKID_GP0_PLL = CLKID_MIPI_DSI_PXCLK = 432000000
    ```

## Buildroot/uInitrd

- [20240706](https://github.com/alexcaoys/notes-superbird/releases/tag/20240706) 
    - Add tar, add resize2fs script, update modules to 6.6.37

- [20240622](https://github.com/alexcaoys/notes-superbird/releases/tag/20240622) 
    - Minor tweaks for vim, update modules to 6.6.35

- [20240619](https://github.com/alexcaoys/notes-superbird/releases/tag/20240619) 
    - Adding tools for resize2fs, FAT and NFS.

- [20240618](https://github.com/alexcaoys/notes-superbird/releases/tag/20240618) 
    - Without FAT and NFS, pair with 20240618 kernel

- [20240614](https://github.com/alexcaoys/notes-superbird/releases/tag/20240614): 
    - uInitrd First release. Pair with 20240610 kernel.