"""ledgercomm.raw_transport module."""

import logging
from typing import Union, Tuple

from ledgercomm.io.tcp_client import TCPClient
from ledgercomm.io.hid_device import HID


class RawTransport:
    """RawTransport factory class to send raw APDUs.

    Allow to communicate using HID device or through TCP
    socket with the Speculos emulator.

    Parameters
    ----------
    hid : bool
        Whether you want to communicate with HID device.
    server : str
        IP adress of the TCP server.
    port : int
        Port of the TCP server.
    debug : bool
        Whether you want debug logs or not.

    Attributes
    ----------
    com : Union[TCPClient, HID]
        Communication interface to send/receive APDUs.

    """

    def __init__(self,
                 hid: bool = False,
                 server: str = "127.0.0.1",
                 port: int = 9999,
                 debug: bool = False) -> None:
        """Init constructor of RawTransport."""
        if debug:
            logging.basicConfig(format="%(message)s", level=logging.DEBUG)

        self.com: Union[TCPClient, HID] = (HID() if hid
                                           else TCPClient(server=server, port=port))

    def send(self, apdus: Union[str, bytes]) -> None:
        """Send `apdus` through `self.com`.

        Parameters
        ----------
        apdus : Union[str, bytes]
            Hexstring or bytes with APDUs to be sent through `self.com`.

        Returns
        -------
        None

        """
        if isinstance(apdus, str):
            apdus = bytes.fromhex(apdus)

        self.com.send(apdus) if apdus else None

    def recv(self) -> Tuple[int, bytes]:
        """Receive data from `self.com`.

        Blocking IO.

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, response) for the status word (2 bytes represented
            as int) and the reponse (bytes of variable lenght).

        """
        return self.com.recv()

    def exchange(self, apdus: Union[str, bytes]) -> Tuple[int, bytes]:
        """Send `apdus` and wait to receive datas from `self.com`.

        Parameters
        ----------
        apdus : Union[str, bytes]
            Hexstring or bytes of APDUs to send through `self.com`.

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, response) for the status word (2 bytes represented
            as int) and the reponse (bytes of variable lenght).

        """
        if isinstance(apdus, str):
            apdus = bytes.fromhex(apdus)

        return self.com.exchange(apdus) if apdus else None

    def close(self) -> None:
        """Close `self.com` interface.

        Returns
        -------
        None

        """
        self.com.close()
