# Release Note

## Latest

- Linux: [6.6.35_20240622](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.35_20240622)

    Using `config_linux_20240622`.

    Sync Kernel with upstream to 6.6.35. 

    Working `panel-sitronix-st7701.c` config: The same as 6.6.32_20240618 below.

- uInitrd: [20240622](https://github.com/alexcaoys/notes-superbird/releases/tag/20240622) 
    - Minor tweaks for vim, update modules to 6.6.35
    - Using `config_buildroot_initrd`. 
    - `ampart` included in `/root`
    - `g_ether` will be enabled at boot. `ssh` is available. 
    - For partitioning only. Pair with 6.6.35_20240622 Kernel.

- Modules folder: [20240622](https://github.com/alexcaoys/notes-superbird/releases/tag/20240622)
    - Pair with 6.6.35_20240622 Kernel.

- Buildroot: W.I.P

## Kernel

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
- [20240619](https://github.com/alexcaoys/notes-superbird/releases/tag/20240619) 
    - Adding tools for resize2fs, FAT and NFS.

- [20240618](https://github.com/alexcaoys/notes-superbird/releases/tag/20240618) 
    - Without FAT and NFS, pair with 20240618 kernel

- [20240614](https://github.com/alexcaoys/notes-superbird/releases/tag/20240614): 
    - uInitrd First release. Pair with 20240610 kernel.