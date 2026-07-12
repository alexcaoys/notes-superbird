import time

import tqdm
import usb.core
import usb.util

# DFU requests
DFU_DETACH = 0
DFU_DNLOAD = 1
DFU_UPLOAD = 2
DFU_GETSTATUS = 3
DFU_CLRSTATUS = 4
DFU_GETSTATE = 5
DFU_ABORT = 6

# DFU states
DFU_STATE_DNLOAD_IDLE = 5
DFU_STATE_DNLOAD_SYNC = 3
DFU_STATE_DNBUSY = 4
DFU_STATE_MANIFEST = 7
DFU_STATE_MANIFEST_WAIT_RESET = 8
DFU_STATE_IDLE = 2

DFU_TIMEOUT = 10000


def detach(dev, intf, timeout):

    result = dev.ctrl_transfer(
        bmRequestType=usb.util.ENDPOINT_OUT
                      | usb.util.CTRL_TYPE_CLASS
                      | usb.util.CTRL_RECIPIENT_INTERFACE,
        bRequest=DFU_DETACH,
        wValue=timeout,
        wIndex=intf.bInterfaceNumber,
        data_or_wLength=b"",
        timeout=DFU_TIMEOUT,
    )


def get_status(dev, intf):
    ret = dev.ctrl_transfer(
        bmRequestType=usb.util.ENDPOINT_IN
                      | usb.util.CTRL_TYPE_CLASS
                      | usb.util.CTRL_RECIPIENT_INTERFACE,
        bRequest=DFU_GETSTATUS,
        wValue=0,
        wIndex=intf.bInterfaceNumber,
        data_or_wLength=6,
        timeout=DFU_TIMEOUT
    )
    status = ret[0]
    poll_timeout = ret[1] | (ret[2] << 8) | (ret[3] << 16)
    state = ret[4]
    return status, poll_timeout, state


def wait_while_busy(dev, intf):
    while True:
        status, poll, state = get_status(dev, intf)

        if status != 0:
            raise RuntimeError(
                f"DFU error status={status}, state={state}"
            )

        if state != DFU_STATE_DNBUSY:
            return state

        time.sleep(poll / 1000)


def download(dev, intf, data, transfer_size=1024):
    block = 0
    offset = 0

    with tqdm.tqdm(
        total=len(data),
        unit="B",
        unit_scale=True, 
        unit_divisor=1024) as pbar:
        while offset < len(data):
            chunk = data[offset:offset + transfer_size]

            dev.ctrl_transfer(
                bmRequestType=usb.util.ENDPOINT_OUT
                            | usb.util.CTRL_TYPE_CLASS
                            | usb.util.CTRL_RECIPIENT_INTERFACE,
                bRequest=DFU_DNLOAD,
                wValue=block,
                wIndex=intf.bInterfaceNumber,
                data_or_wLength=chunk,
                timeout=DFU_TIMEOUT
            )

            state = wait_while_busy(dev, intf)

            if state not in (
                DFU_STATE_DNLOAD_SYNC,
                DFU_STATE_DNLOAD_IDLE,
            ):
                raise RuntimeError(
                    f"Unexpected state {state}"
                )

            pbar.update(transfer_size)
            offset += len(chunk)
            block += 1

    # EOF
    dev.ctrl_transfer(
        bmRequestType=usb.util.ENDPOINT_OUT
                    | usb.util.CTRL_TYPE_CLASS
                    | usb.util.CTRL_RECIPIENT_INTERFACE,
        bRequest=DFU_DNLOAD,
        wValue=block,
        wIndex=intf.bInterfaceNumber,
        data_or_wLength=b"",
        timeout=DFU_TIMEOUT
    )

    wait_while_busy(dev, intf)


def find_dfu_alt(dev, alt):
    for cfg in dev:
        for intf in cfg:
            if intf.bInterfaceClass == 0xFE and \
               intf.bInterfaceSubClass == 0x01 and \
               intf.bAlternateSetting == alt:
                return cfg, intf

    raise ValueError(f"DFU alt {alt} not found")


def dfu_detach(
    vid,
    pid,
    alt=0,
):
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if dev is None:
        raise RuntimeError("Device not found")

    cfg, intf = find_dfu_alt(dev, alt)

    if dev.is_kernel_driver_active(intf.bInterfaceNumber):
        dev.detach_kernel_driver(intf.bInterfaceNumber)

    usb.util.claim_interface(dev, intf.bInterfaceNumber)

    try:
        detach(dev, intf, 1000)
    finally:
        usb.util.release_interface(
            dev,
            intf.bInterfaceNumber,
        )


def dfu_download(
    vid,
    pid,
    file_path,
    alt=0,
    transfer_size=1024,
):
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if dev is None:
        raise RuntimeError("Device not found")

    cfg, intf = find_dfu_alt(dev, alt)

    if dev.is_kernel_driver_active(intf.bInterfaceNumber):
        dev.detach_kernel_driver(intf.bInterfaceNumber)

    usb.util.claim_interface(dev, intf.bInterfaceNumber)

    try:
        dev.set_interface_altsetting(
            interface=intf.bInterfaceNumber,
            alternate_setting=alt,
        )

        with open(file_path, "rb") as f:
            image = f.read()

        download(dev, intf, image, transfer_size)

    finally:
        usb.util.release_interface(
            dev,
            intf.bInterfaceNumber,
        )


def dfu_list():
    list_dfu_dev = list()
    for dev in usb.core.find(find_all=True):
        for cfg in dev:
            for intf in cfg:
                if intf.bInterfaceClass == 0xFE and \
                    intf.bInterfaceSubClass == 0x01:
                    list_dfu_dev.append({
                        "idVendor": f"{dev.idVendor:04x}",
                        "idProduct": f"{dev.idProduct:04x}",
                        "bcdDevice": f"{dev.bcdDevice:04x}",
                        "iManufacturer": dev.iManufacturer,
                        "iProduct": dev.iProduct,
                        "iSerialNumber": dev.iSerialNumber,
                        "bConfigurationValue": cfg.bConfigurationValue,
                        "bInterfaceNumber": intf.bInterfaceNumber,
                        "bAlternateSetting": intf.bAlternateSetting,
                        "iInterface": intf.iInterface,
                    })
    return list_dfu_dev