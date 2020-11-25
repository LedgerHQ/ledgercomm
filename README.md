# LedgerCOMM

## Overview

Python library to send and receive [APDU](https://en.wikipedia.org/wiki/Smart_card_application_protocol_data_unit) through HID or TCP socket.
It can be used with a Ledger Nano S/X or with the [Speculos](https://github.com/LedgerHQ/speculos) emulator.

## Install

If you just want to communicate through TCP socket, there is no dependency

```bash
$ pip install ledgercomm
```

otherwise, [hidapi](https://github.com/trezor/cython-hidapi) must be installed as an extra dependency like this

```bash
$ pip install ledgercomm[hid]
```

## Getting started

### Library

```python
from ledgercomm import Transport

# Nano S/X using HID interface
transport = Transport(interface="hid", debug=True)
# or Speculos through TCP socket
transport = Transport(interface="tcp", server="127.0.0.1", port=9999, debug=True)

#
# send/recv APDUs
#

# send method for structured APDUs
transport.send(cla=0xe0, ins=0x03, p1=0, p2=0, cdata=b"")  # send b"\xe0\x03\x00\x00\x00"
# or send_raw method for hexadecimal string
transport.send_raw("E003000000")  # send b"\xe0\x03\x00\x00\x00"
# or with bytes type
transport.send_raw(b"\xe0\x03\x00\x00\x00")

# Waiting for a response (blocking IO)
sw, response = transport.recv()  # type: int, bytes

#
# exchange APDUs (one time send/recv)
#

# exchange method for structured APDUs
sw, response = transport.exchange(cla=0xe0, ins=0x03, p1=0, p2=0, cdata=b"")  # send b"\xe0\x03\x00\x00\x00"
# or exchange_raw method for hexadecimal string
sw, reponse = transport.exchange_raw("E003000000")  # send b"\xe0\x03\x00\x00\x00"
# or with bytes type
sw, response = transport.exchange_raw(b"\xe0\x03\x00\x00\x00")

```

### CLI

#### Usage

When installed, `ledgercomm` provides a CLI tool named `ledgercomm-send`

```bash
$ ledgercomm-send --help
usage: ledgercomm-send [-h] [--hid] [--server SERVER] [--port PORT] [--startswith STARTSWITH]
                       {file,stdin,log} ...

positional arguments:
  {file,stdin,log}      sub-command help
    file                send APDUs from file
    stdin               send APDUs from stdin
    log                 send APDUs from Ledger Live log file

optional arguments:
  -h, --help            show this help message and exit
  --hid                 Use HID instead of TCP client
  --server SERVER       IP server of the TCP client (default: 127.0.0.1)
  --port PORT           Port of the TCP client (default: 9999)
  --startswith STARTSWITH
                        Only send APDUs starting with STARTSWITH (default: None)
```

#### Example

If Speculos is launched with default parameters or your Nano S/X is plugged with correct udev rules, you can send APDUs from stdin

```bash
$ echo "E003000000" | ledgercomm-send stdin  # Speculos
$ echo "E003000000" | ledgercomm-send --hid stdin  # Nano S/X
```

Or you can replay APDUs using the following text file named `apdus.txt` with some condition

```text
# this line won't be send if you've the right STARTSWITH condition
=> E003000000
# another APDU to send
=> E004000000
```

then

```bash
$ ledgercomm-send --startswith "=>" file apdus.txt
```
