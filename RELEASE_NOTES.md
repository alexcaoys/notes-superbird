# Release Note

## Latest

- Linux: `config_linux_20240616`

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

- uInitrd: [20240617](https://github.com/alexcaoys/notes-superbird/releases/tag/20240617) 

    - Using `config_buildroot_initrd`, removed most package to fit in RAM. 
    - `ampart` included in `/root`
    - `g_ether` will be enabled at boot. `ssh` is also available. 
    - For partitioning only. 

- Buildroot: W.I.P

## Kernel

- Linux: `config_linux_20240610`

    First release. Available as Image and dts [here](https://github.com/alexcaoys/linux-superbird-6.6.y/releases/tag/6.6.32_20240610). This image doesn't have the working panel config. So the display won't have the correct color.

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

- 20240614: uInitrd First release. Available as image. Will release another version pretty soon. [Link](https://github.com/alexcaoys/notes-superbird/releases/tag/20240614) 