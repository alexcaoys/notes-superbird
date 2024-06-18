import time
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
    WRITE_CHUNK_SIZE =    1024 * PART_SECTOR_SIZE  # 512KB chunk written to memory, then gets written to mmc
    READ_CHUNK_SIZE =     256 * PART_SECTOR_SIZE  # 128KB chunk read from mmc into memory, then read out to local file

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

    def read_memory(self, address, length):
        """Read some data from memory"""
        data = None
        offset = 0
        while length:
            if length >= 64:
                read_data = self.device.readSimpleMemory(address + offset, 64).tobytes()
                if data is not None:
                    data = data + read_data
                else:
                    data = read_data
                length = length - 64
                offset = offset + 64
            else:
                read_data = self.device.readSimpleMemory(address + offset, length).tobytes()
                if data is not None:
                    data = data + read_data
                else:
                    data = read_data
                break
        return data

    # def addr_dump(part_name, hex_start, hex_size, outfile):
    #     chunk_size = READ_CHUNK_SIZE
    #     with open(outfile, 'wb') as ofl:
    #         offset = 0
    #         first_chunk = True
    #         last_chunk = False
    #         remaining = part_size
    #         start_time = time.time()
    #         while remaining:
    #             if first_chunk:
    #                 first_chunk = False
    #             else:
    #                 stdout_clear_lines(2)
    #             if remaining <= chunk_size:
    #                 chunk_size = remaining
    #                 last_chunk = True
    #             progress = round((offset / part_size) * 100)
    #             elapsed = time.time() - start_time
    #             if elapsed < 1:
    #                 # on a quick enough system, elapsed can be zero, and cause divbyzero error when calculating speed
    #                 speed = 0
    #             else:
    #                 speed = round((offset / elapsed) / 1024)  # in KB/s
    #             print(f'dumping {hex(part_offset)}+{hex(offset)} into file: {outfile} ')
    #             print(f'chunk_size: {chunk_size / 1024}KB, speed: {speed}KB/s progress: {progress}% remaining: {round(remaining / 1024)}KB / {round(part_size / 1024)}KB')
    #             bulkcmd(f'amlmmc read {part_name} {hex(ADDR_TMP)} {hex(offset)} {hex(chunk_size)}', silent=True)
    #             rdata = self.read_memory(self.ADDR_TMP, chunk_size)
    #             ofl.raw.write(rdata)
    #             ofl.flush()
    #             if last_chunk:
    #                 break
    #             offset += chunk_size
    #             remaining -= chunk_size

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

    def boot(self, env_file:str, kernel:str, initrd:str="", dtb:str=""):
        """ boot using given env.txt, kernel, kernel address, and initrd, intitrd_address """
        print(f'Booting {env_file=}, {kernel=}, {initrd=}, {dtb=}')
        self.send_env_file(env_file)
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
    parser.add_argument('-s', '--stock', action='store_true')
    parser.add_argument('-c', '--custom', action='store_true')
    parser.add_argument('-i', '--initrd', action='store_true')
    parser.add_argument('-b', '--bulkcmd')
    args = parser.parse_args()

    ad = AmlogicDevice()

    if args.custom:
        env_file = "envs/env_b.txt"
        kernel = "Image"
        #initrd = "uInitrd"
        dtb = "meson-g12a-superbird.dtb"
        ad.boot(env_file, kernel, "", dtb)

    elif args.initrd:
        env_file = "envs/env_initrd.txt"
        kernel = "Image"
        initrd = "uInitrd"
        dtb = "meson-g12a-superbird.dtb"
        ad.boot(env_file, kernel, initrd, dtb)

    elif args.stock:
        ad.bulkcmd("run init_display;run storeboot;")

    elif args.bulkcmd:
        ad.bulkcmd(args.bulkcmd)
