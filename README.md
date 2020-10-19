# LedgerCOMM

## Overview

Python library to send and receive [APDU](https://en.wikipedia.org/wiki/Smart_card_application_protocol_data_unit) through HID or TCP socket.
It could be used with a Ledger Nano S/X or with the [Speculos](https://github.com/LedgerHQ/speculos) emulator.

## Install

If you just want to communicate through TCP socket, there is no dependency:

```bash
pip install ledgercomm
```

otherwise, [hidapi](https://github.com/trezor/cython-hidapi) must be installed as an extra dependency:

```bash
pip install ledgercomm[hid]
```

## Usage

### Nano S/X

```python
from ledgercomm import RawTransport, Transport

#
# use RawTransport to send raw APDUs
#
transport = RawTransport(hid=True, debug=True)

# send method using hexadecimal string
transport.send("03000000")  # send b"\x03\x00\x00\x00"
# send can also be used with bytes
transport.send(b"\x03\x00\x00\x00")

#
# use Transport to send structured APDUs
#
transport = Transport(hid=True, debug=True)

# send method using structured APDU
transport.send(cla=3, ins=0, p1=0, p2=0, payload=b"")  # send b"\x03\x00\x00\x00"
```

### Speculos

```python
from ledgercomm import RawTransport, Transport

#
# use RawTransport to send raw APDUs
#
transport = RawTransport(server="127.0.0.1", port=9999, debug=True)

# send either hexadecimal string or bytes
transport.send("03000000")

#
# use Transport to send structured APDUs
#
transport = Transport(server="127.0.0.1", port=9999, debug=True)


transport.send(cla=3, ins=0, p1=0, p2=0, payload=b"\x00")
```
