from ledgercomm import Transport


class LedgerAppConfiguration:
    data_activated: bool
    account_index: int
    address_index: int
    version: str


def load_ledger_config_from_response(response: bytes) -> LedgerAppConfiguration:
    config = LedgerAppConfiguration()

    config.data_activated = False
    if response[0] == 0x01:
        config.data_activated = True

    config.account_index = response[1]
    config.address_index = response[2]

    version = str(response[3]) + "." + str(response[4]) + "." + str(response[5])
    config.version = version

    return config


def get_error(code: int):
    switcher = {
        0x9000: '',
        0x6985: 'user denied',
        0x6D00: 'unknown instruction',
        0x6E00: 'wrong cla',
        0x6E10: 'signature failed',
        0x6E01: 'invalid arguments',
        0x6E02: 'invalid message',
        0x6E03: 'invalid p1',
        0x6E04: 'message too long',
        0x6E05: 'receiver too long',
        0x6E06: 'amount too long',
        0x6E07: 'contract data disabled',
        0x6E08: 'message incomplete',
        0x6E09: 'wrong tx version',
        0x6E0A: 'nonce too long',
        0x6E0B: 'invalid amount',
        0x6E0C: 'invalid fee',
        0x6E0D: 'pretty failed',
        0x6E0E: 'data too long',
        0x6E0F: 'wrong tx options',
        0x6E11: 'regular signing is deprecated',
    }

    return switcher.get(code, "unknown error code: " + hex(code))


def main():
    transport = Transport(interface="hid", debug=True)
    transport.send(cla=0xed, ins=0x02, p1=0x00, p2=0x00, cdata=b"")
    sw, response = transport.recv()
    print(f"sw: {sw}")
    print("Error:", get_error(sw))
    print(f"response: {response}")

    if response:
        config = load_ledger_config_from_response(response)
        print(f"config: {config.__dict__}")


if __name__ == "__main__":
    main()
