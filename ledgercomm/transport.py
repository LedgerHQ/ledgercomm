"""ledgercomm.transport module."""

import enum
import logging
import struct
from typing import Union, Tuple, Optional, cast

from ledgercomm.io.tcp_client import TCPClient
from ledgercomm.io.hid_device import HID


class Transport:
    """Transport factory class to send structured APDUs.

    Allow to communicate using HID device or through TCP
    socket with the Speculos emulator.

    Parameters
    ----------
    hid : bool
        Whether you want to communicate with HID interface.
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
        """Init constructor of Transport."""
        if debug:
            logging.basicConfig(format="%(message)s", level=logging.DEBUG)

        self.com: Union[TCPClient, HID] = (HID() if hid
                                           else TCPClient(server=server, port=port))

    @staticmethod
    def get_header(cla: int,
                   ins: Union[int, enum.IntEnum],
                   p1: int = 0,
                   p2: int = 0,
                   opt: Optional[int] = None,
                   lc: int = 0) -> bytes:
        """Pack the APDU header as bytes.

        Parameters
        ----------
        cla : int
            Instruction class: CLA (1 byte)
        ins : Union[int, IntEnum]
            Instruction code: INS (1 byte)
        p1 : int
            Instruction parameter: P1 (1 byte).
        p2 : int
            Instruction parameter: P2 (1 byte).
        opt : Optional[int]
            Optional parameter: Opt (1 byte).
        lc : int
            Number of bytes in the payload: Lc (1 byte).

        Returns
        -------
        bytes
            Header packed with parameters.

        """
        ins = cast(int, ins.value) if isinstance(ins, enum.IntEnum) else cast(int, ins)

        if opt:
            return struct.pack("BBBBBB",
                               cla,
                               ins,
                               p1,
                               p2,
                               1 + lc,  # add option to length
                               opt)

        return struct.pack("BBBBB",
                           cla,
                           ins,
                           p1,
                           p2,
                           lc)

    def send(self,
             cla: int,
             ins: Union[int, enum.IntEnum],
             p1: int = 0,
             p2: int = 0,
             opt: Optional[int] = None,
             payload: bytes = b"") -> None:
        """Send structured APDUs through `self.com`.

        Parameters
        ----------
        cla : int
            Instruction class: CLA (1 byte)
        ins : Union[int, IntEnum]
            Instruction code: INS (1 byte)
        p1 : int
            Instruction parameter: P1 (1 byte).
        p2 : int
            Instruction parameter: P2 (1 byte).
        opt : Optional[int]
            Optional parameter: Opt (1 byte).
        payload : bytes
            Payload to send (bytes of variable length).

        Returns
        -------
        None

        """
        header: bytes = Transport.get_header(cla, ins, p1, p2, opt, len(payload))

        self.com.send(header + payload)

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

    def exchange(self,
                 cla: int,
                 ins: Union[int, enum.IntEnum],
                 p1: int = 0,
                 p2: int = 0,
                 option: Optional[int] = None,
                 payload: bytes = b"") -> Tuple[int, bytes]:
        """Send structured APDUs and wait to receive datas from `self.com`.

        Parameters
        ----------
        cla : int
            Instruction class: CLA (1 byte)
        ins : Union[int, IntEnum]
            Instruction code: INS (1 byte)
        p1 : int
            Instruction parameter: P1 (1 byte).
        p2 : int
            Instruction parameter: P2 (1 byte).
        opt : Optional[int]
            Optional parameter: Opt (1 byte).
        payload : bytes
            Payload to send (bytes of variable length).

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, response) for the status word (2 bytes represented
            as int) and the reponse (bytes of variable lenght).

        """
        header: bytes = Transport.get_header(cla, ins, p1, p2, option, len(payload))

        return self.com.exchange(header + payload)

    def close(self) -> None:
        """Close `self.com` interface.

        Returns
        -------
        None

        """
        self.com.close()
