"""ledgercomm.interfaces.tcp_client module."""

import logging
import socket
from typing import Tuple

from ledgercomm.interfaces.comm import Comm


class TCPClient(Comm):
    """TCPClient class.

    Mainly used to connect to the TCP server of the Speculos emulator.

    Parameters
    ----------
    server : str
        IP address of the TCP server.
    port : int
        Port of the TCP server.

    Attributes
    ----------
    server : str
        IP address of the TCP server.
    port : int
        Port of the TCP server.
    socket : socket.socket
        TCP socket to communicate with the server.
    __opened : bool
        Whether the TCP socket is opened or not.

    """

    def __init__(self, server: str, port: int) -> None:
        """Init constructor of TCPClient."""
        self.server: str = server
        self.port: int = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__opened: bool = False

    def open(self) -> None:
        """Open connection to TCP socket with `self.server` and `self.port`.

        Returns
        -------
        None

        """
        if not self.__opened:
            self.socket.connect((self.server, self.port))
            self.__opened = True

    def send(self, data: bytes) -> int:
        """Send `data` through TCP socket `self.socket`.

        Parameters
        ----------
        data : bytes
            Bytes with `data` to send.

        Returns
        -------
        int
            Total lenght of data sent through TCP socket.

        """
        if not data:
            raise Exception("Can't send empty data!")

        logging.debug("=> %s", data.hex())
        data_len: bytes = int.to_bytes(len(data), 4, byteorder="big")

        return self.socket.send(data_len + data)

    def recv(self) -> Tuple[int, bytes]:
        """Receive data through TCP socket `self.socket`.

        Blocking IO.

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, data) containing the status word and associated datas.

        """
        length: int = int.from_bytes(self.socket.recv(4), byteorder="big")
        data: bytes = self.socket.recv(length)
        sw: int = int.from_bytes(self.socket.recv(2), byteorder="big")

        logging.debug("<= %s %s", data.hex(), hex(sw)[2:])

        return sw, data

    def exchange(self, data: bytes) -> Tuple[int, bytes]:
        """Exchange (send + receive) with `self.socket`.

        Parameters
        ----------
        data : bytes
            Bytes with `data` to send.

        Returns
        -------
        Tuple[int, bytes]
            A pair (sw, data) containing the status word and associated datas.

        """
        self.send(data)

        return self.recv()  # blocking IO

    def close(self) -> None:
        """Close connection to TCP socket `self.socket`.

        Returns
        -------
        None

        """
        if self.__opened:
            self.socket.close()
            self.__opened = False
