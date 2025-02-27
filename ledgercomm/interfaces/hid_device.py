"""ledgercomm.interfaces.hid_device module."""

from typing import Any, List, Mapping, Optional, Tuple

try:
    import hid
except ImportError:
    hid = None

from ledgercomm.interfaces.comm import Comm
from ledgercomm.log import LOG

DEFAULT_VENDOR_ID = 0x2C97
MACOS_USAGE_PAGE = 0xFFA0


class HIDAPINotInstalledError(ImportError):
    """Custom error to be raised when hidapi is not installed."""

    def __init__(self):
        """Init constructor of HIDAPINotInstalledError."""
        super().__init__("hidapi is not installed, try: 'pip install ledgercomm[hid]'")


class CannotFindDeviceError(Exception):
    """Custom error to be raised when the device can't be found."""

    def __init__(self, vendor_id: int):
        """Init constructor of CannotFindDeviceError."""
        super().__init__(f"Can't find Ledger device with vendor_id {hex(vendor_id)}")


class HID(Comm):
    """HID class.

    Mainly used to communicate with Nano S/X through USB.

    Parameters
    ----------
    vendor_id: int
        Vendor ID of the device. Default to Ledger Vendor ID 0x2C97.

    Attributes
    ----------
    device : hid.device
        HID device connection.
    path : Optional[bytes]
        Path of the HID device.
    __opened : bool
        Whether the connection to the HID device is opened or not.

    """

    def __init__(self, vendor_id: int = DEFAULT_VENDOR_ID) -> None:
        """Init constructor of HID."""
        if hid is None:
            raise HIDAPINotInstalledError()

        self.device = hid.device()
        self.path: Optional[bytes] = None
        self.__opened: bool = False
        self.vendor_id: int = vendor_id

    def open(self) -> None:
        """Open connection to the HID device.

        Returns
        -------
        None

        """
        if not self.__opened:
            if not self.path:
                self.path = HID._decide_device_path(self.vendor_id)
            self.device.open_path(self.path)
            self.device.set_nonblocking(True)
            self.__opened = True

    @staticmethod
    def _decide_device_path(vendor_id: int = DEFAULT_VENDOR_ID) -> bytes:
        if hid is None:
            raise HIDAPINotInstalledError()

        devices: List[Mapping[str, Any]] = list(hid.enumerate(vendor_id, 0))
        LOG.debug("hid.enumerate(), devices: %s", devices)

        devices = [device for device in devices if device.get("interface_number") == 0]
        if len(devices) == 1:
            # No ambiguity, pick the only device
            return devices[0]["path"]

        # On MacOS, "interface_number" is not a reliable filtering criteria, so we
        # also filter by "usage_page".
        mac_filtered_devices = [
            device for device in devices if device.get("usage_page") == MACOS_USAGE_PAGE
        ]
        if len(mac_filtered_devices) != 0:
            # If we are on a MAC device, we keep the new filtered list
            devices = mac_filtered_devices
        if len(devices) == 1:
            # No ambiguity, pick the only device
            return devices[0]["path"]

        if len(devices) > 1:
            LOG.warning(
                "More than one Ledger device with vendor_id %s, will pick the first one",
                hex(vendor_id),
            )

            # First, we sort by "path", so that the order is deterministic
            devices = sorted(devices, key=lambda device: device["path"])
            return devices[0]["path"]

        raise CannotFindDeviceError(vendor_id)

    @staticmethod
    def enumerate_devices(vendor_id: int = DEFAULT_VENDOR_ID) -> List[bytes]:
        """Enumerate HID devices to find Nano S/X.

        Parameters
        ----------
        vendor_id: int
            Vendor ID of the device. Default to Ledger Vendor ID 0x2C97.

        Returns
        -------
        List[bytes]
            List of paths to HID devices which should be Nano S or Nano X.

        """
        if hid is None:
            raise HIDAPINotInstalledError()

        devices: List[bytes] = []

        for hid_device in hid.enumerate(vendor_id, 0):
            if (
                hid_device.get("interface_number") == 0
                or
                # MacOS specific
                hid_device.get("usage_page") == MACOS_USAGE_PAGE
            ):
                devices.append(hid_device["path"])

        assert len(devices) != 0, f"Can't find Ledger device with vendor_id {hex(vendor_id)}"

        return devices

    def send(self, data: bytes) -> int:
        """Send `data` through HID device `self.device`.

        Parameters
        ----------
        data : bytes
            Bytes of data to send.

        Returns
        -------
        int
            Total length of data sent to the device.

        """
        if not data:
            raise ValueError("Can't send empty data!")

        LOG.debug("=> %s", data.hex())

        data = int.to_bytes(len(data), 2, byteorder="big") + data
        offset: int = 0
        seq_idx: int = 0
        length: int = 0

        while offset < len(data):
            # Header: channel (0x0101), tag (0x05), sequence index
            header: bytes = b"\x01\x01\x05" + seq_idx.to_bytes(2, byteorder="big")
            data_chunk: bytes = header + data[offset : offset + 64 - len(header)]

            self.device.write(b"\x00" + data_chunk)
            length += len(data_chunk) + 1
            offset += 64 - len(header)
            seq_idx += 1

        return length

    def recv(self) -> Tuple[int, bytes]:
        """Receive data through HID device `self.device`.

        Blocking IO.

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, rdata) containing the status word and response data.

        """
        seq_idx: int = 0
        self.device.set_nonblocking(False)
        data_chunk: bytes = bytes(self.device.read(64 + 1))
        self.device.set_nonblocking(True)

        assert data_chunk[:2] == b"\x01\x01"
        assert data_chunk[2] == 5
        assert data_chunk[3:5] == seq_idx.to_bytes(2, byteorder="big")

        data_len: int = int.from_bytes(data_chunk[5:7], byteorder="big")
        data: bytes = data_chunk[7:]

        while len(data) < data_len:
            read_bytes = bytes(self.device.read(64 + 1, timeout_ms=1000))
            data += read_bytes[5:]

        sw: int = int.from_bytes(data[data_len - 2 : data_len], byteorder="big")
        rdata: bytes = data[: data_len - 2]

        LOG.debug("<= %s %s", rdata.hex(), hex(sw)[2:])

        return sw, rdata

    def exchange(self, data: bytes) -> Tuple[int, bytes]:
        """Exchange (send + receive) with `self.device`.

        Parameters
        ----------
        data : bytes
            Bytes with `data` to send.

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, rdata) containing the status word and response data.

        """
        self.send(data)

        return self.recv()  # blocking IO

    def close(self) -> None:
        """Close connection to HID device `self.device`.

        Returns
        -------
        None

        """
        if self.__opened:
            self.device.close()
            self.__opened = False
