import os
import sys
import time
import traceback
from argparse import ArgumentParser

from pyamlboot import pyamlboot


class AmlogicDevice:
    ADDR_BL2 =    0xfffa0000
    ADDR_KERNEL = 0x01080000
    ADDR_INITRD = 0x10000000
    ADDR_DTB =    0x01000000
    ADDR_TMP =    0x13000000

    PART_SECTOR_SIZE =    512  # bytes, size of sectors used in partition table
    TRANSFER_BLOCK_SIZE = 8 * PART_SECTOR_SIZE  # 4KB data transfered into memory one block at a time
    WRITE_CHUNK_SIZE =    4096  # 2MB chunk written to memory, then gets written to mmc
    TRANSFER_SIZE_THRESHOLD = 2 * 1024 * 1024  # 2MB

    def __init__(self) -> None:
        self.device = pyamlboot.AmlogicSoC()

    def bulkcmd(self, command:str):
        r = self.device.bulkCmd(command)
        response = r.tobytes().decode("utf-8")
        print(f'result: {response}')
        if 'success' not in response:
            print(f'bulkcmd failed: {command} -> {response}')
        time.sleep(0.2)

    def write(self, address:int, data, chunk_size=8, append_zeros=True):
        """ write data to an address """
        print(f' writing to: {hex(address)}')
        self.device.writeLargeMemory(address, data, chunk_size, append_zeros)

    def send_env(self, env_string:str):
        """ send given env string to device, space-separated kernel args on one line """
        env_size = len(env_string.encode('ascii'))
        print('initializing env subsystem')
        self.bulkcmd('amlmmc env')  # initialize env subsystem
        print(f'sending env ({env_size} bytes)')
        self.write(self.ADDR_TMP, env_string.encode('ascii'))  # write env string somewhere
        self.bulkcmd(f'env import -t {hex(self.ADDR_TMP)} {hex(env_size)}')  # read env from string

    def send_env_file(self, env_file:str):
        """ read env.txt, then send it to device """
        env_data = ''
        with open(env_file, 'r', encoding='utf-8') as envf:
            env_data = envf.read()
        self.send_env(env_data)

    def send_file(self, filepath:str, address:int, chunk_size:int=1024, append_zeros=True):
        """ write given file to device memory at given address """
        print(f'writing {filepath} at {hex(address)}')
        file_data = None
        with open(filepath, 'rb') as flp:
            file_data = flp.read()
        self.write(address, file_data, chunk_size, append_zeros)

    def restore_partition(self, part_offset:int, infile:str):
        """ Restore given partition from given dump
            Like with dump_partition, we first have to read it into RAM, then instruct the device to write it to mmc, one chunk at a time
        """
        if part_offset < 319488:
            print("WARNING: You might be writing to reserved partitions!!!")
        input(f"Press any key to confirm: write {infile} to mmc offset {hex(part_offset)}")
        self.bulkcmd('amlmmc part 1')
        try:
            chunk_size_sector = self.WRITE_CHUNK_SIZE
            chunk_size = self.WRITE_CHUNK_SIZE * self.PART_SECTOR_SIZE
            file_size = os.path.getsize(infile)
            with open(infile, 'rb') as ifl:
                # now we are ready to actually write to the partition
                offset = 0
                last_chunk = False
                remaining = file_size
                
                while remaining:
                    if remaining <= chunk_size:
                        # chunk_size = remaining
                        last_chunk = True
                    progress = round((offset * 512 / file_size) * 100)
                    data = ifl.read(chunk_size)
                    remaining -= chunk_size
                    print(f'writing to emmc: {hex(part_offset)}+{hex(offset)} from file: {infile}')
                    print(f'progress: {progress}% remaining: {round(remaining / 1024 / 1024)}MB / {round(file_size / 1024 / 1024)}MB, chunk_size: {chunk_size / 1024}KB')
                    self.device.writeLargeMemory(self.ADDR_TMP, data, self.TRANSFER_BLOCK_SIZE, appendZeros=True)
                    self.bulkcmd(f'amlmmc write 1 {hex(self.ADDR_TMP)} {hex(part_offset+offset)} {hex(chunk_size_sector)}')
                    offset += chunk_size_sector
                    if last_chunk:
                        break
        except Exception as e:
            # in the event of any failure while writing partitions,
            #   force the entire script to exit to prevent further possible damage
            print(f'Error while restoring partition {e}')
            print(traceback.format_exc())
            sys.exit(1)

    def boot(self, memory:bool, env_file:str, kernel="", initrd="", dtb=""):
        """ boot using given env.txt, kernel, dtb and initrd"""
        self.send_env_file(env_file)
        if memory:
            print(f'Booting from memory {env_file=}, {self.ADDR_KERNEL=}, {self.ADDR_INITRD=}, {self.ADDR_DTB=}')
            cmd = f'booti {hex(self.ADDR_KERNEL)}'
            if initrd:
                cmd += f" {hex(self.ADDR_INITRD)}"
            if dtb:
                if not initrd:
                    cmd += f" -"
                cmd += f" {hex(self.ADDR_DTB)}"
        else:
            print(f'Booting {env_file=}, {kernel=}, {initrd=}, {dtb=}')
            self.send_file(kernel, self.ADDR_KERNEL)
            cmd = f'booti {hex(self.ADDR_KERNEL)}'
            if initrd:
                self.send_file(initrd, self.ADDR_INITRD)
                cmd += f" {hex(self.ADDR_INITRD)}"
            if dtb:
                self.send_file(dtb, self.ADDR_DTB)
                if not initrd:
                    cmd += f" -"
                cmd += f" {hex(self.ADDR_DTB)}"
        try:
            self.bulkcmd(cmd)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-b', '--bulkcmd')
    parser.add_argument('-s', '--stock', action='store_true')
    parser.add_argument('-r', '--restore', nargs=2, metavar=('PART_OFFSET', 'INPUT_FILE'))
    parser.add_argument('-m', '--memory', nargs=1, metavar=('ENV_FILE'))
    parser.add_argument('-c', '--custom', nargs=3, metavar=('ENV_FILE', 'KERNEL_PATH', 'DTB_PATH'))
    parser.add_argument('-i', '--initrd', nargs=4, metavar=('ENV_FILE', 'KERNEL_PATH', 'INITRD_PATH', 'DTB_PATH'))
    args = parser.parse_args()

    ad = AmlogicDevice()

    if args.bulkcmd:
        ad.bulkcmd(args.bulkcmd)
    elif args.stock:
        ad.bulkcmd("run init_display;run storeboot;")
    elif args.restore:
        try:
            part_offset = int(args.restore[0])
            file = args.restore[1]
        except ValueError:
            print("part_offset need to be integer.")
            sys.exit(1)
        ad.restore_partition(part_offset, file)
    elif args.memory:
        # env_file = "envs/env_custom_partition.txt"
        ad.boot(True, args.memory[0])
    elif args.custom:
        # env_file = "envs/env_b.txt"
        # kernel = "Image"
        # #initrd = "uInitrd"
        # dtb = "meson-g12a-superbird.dtb"
        ad.boot(False, args.custom[0], args.custom[1], "", args.custom[2])
    elif args.initrd:
        # env_file = "envs/env_initrd.txt"
        # kernel = "Image"
        # initrd = "uInitrd"
        # dtb = "meson-g12a-superbird.dtb"
        ad.boot(False, args.initrd[0], args.initrd[1], args.initrd[2], args.initrd[3])