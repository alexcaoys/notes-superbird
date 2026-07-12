import os
import sys
import time
import traceback
from argparse import ArgumentParser

from pyamlboot import pyamlboot

ADDR_BL2 =    0xfffa0000
ADDR_KERNEL = 0x01080000
ADDR_INITRD = 0x10000000
ADDR_DTB =    0x01000000
ADDR_TMP =    0x13000000

def send_file(device, filepath:str, address:int, chunk_size:int=1024, append_zeros=True, bl2=False):
    """ write given file to device memory at given address """
    with open(filepath, 'rb') as f:
        data = f.read()

    if bl2:
        data_write = data[0:0x10000]
    else:
        data_write = data

    print(f'writing {filepath} at {hex(address)}')
    device.writeLargeMemory(address, data_write, chunk_size, append_zeros)
    print("[DONE]")

    return data

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('uboot')
    parser.add_argument('--kernel')
    parser.add_argument('--dtb')
    parser.add_argument('--initramfs')
    parser.add_argument('--fitimage')
    parser.add_argument('--bl2')
    args = parser.parse_args()

    dev = pyamlboot.AmlogicSoC()

    socid = dev.identify()

    print("Firmware Version :")
    print("ROM: %d.%d Stage: %d.%d" % (ord(socid[0]), ord(socid[1]), ord(socid[2]), ord(socid[3])))
    print("Need Password: %d Password OK: %d" % (ord(socid[4]), ord(socid[5])))

    print(f'Booting {args.uboot=}, {args.kernel=}, {args.dtb=}, {args.initramfs=}, {args.bl2=}')
    seq = 0

    with open(args.uboot, 'rb') as f:
        data = f.read()
    
    if args.bl2:
        with open(args.bl2, 'rb') as f:
            data_bl2 = f.read()
        data = data_bl2[0:0x10000] + data[0x10000:]

    print(f'writing bl2 at {hex(ADDR_BL2)}')
    dev.writeLargeMemory(ADDR_BL2, data[0:0x10000], 4096)
    print("[DONE]")

    print("Running at 0x%x..." % ADDR_BL2)
    dev.run(0xfffa0000)
    print("[DONE]")

    time.sleep(2)

    prevLength = -1
    prevOffset = -1
    while True:
        (length, offset) = dev.getBootAMLC()

        if length == prevLength and offset == prevOffset:
            print("[BL2 END]")
            break

        prevLength = length
        prevOffset = offset

        print("AMLC dataSize=%d, offset=%d, seq=%d..." % (length, offset, seq))
        dev.writeAMLCData(seq, offset, data[offset:offset+length])
        print("[DONE]")

        seq = seq + 1

    if args.fitimage or args.kernel or args.dtb or args.initramfs:
        from pydfu import dfu_download, dfu_detach, dfu_list
        
        print("u-boot DFU init")
        retry = 0
        done = False
        while retry < 5:
            print(f"u-boot DFU retry: {retry}")

            if not dfu_list():
                retry += 1
                time.sleep(5)
                continue

            if args.fitimage:
                dfu_download(0x1b8e, 0xfada, args.fitimage, 3)
            else:
                if args.kernel:
                    dfu_download(0x1b8e, 0xfada, args.kernel, 0)
                if args.dtb:
                    dfu_download(0x1b8e, 0xfada, args.dtb, 1)
                if args.initramfs:
                    dfu_download(0x1b8e, 0xfada, args.initramfs, 2)
            dfu_detach(0x1b8e, 0xfada)
            done = True
            print("[DONE]")
            break
        if not done:
            print("Something is wrong. Please try again")