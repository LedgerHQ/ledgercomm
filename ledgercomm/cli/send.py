"""ledgercomm.cli.send module."""

import argparse
from pathlib import Path
import re
from typing import Iterator, Optional

from ledgercomm import Transport


def parse_file(filepath: Path, condition: Optional[str]) -> Iterator[str]:
    """Filter with `condition` and yield line of `filepath`."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if condition and line.startswith(condition):
                yield line.replace(condition, "").strip()
            else:
                yield line.strip()


def main():
    """Entrypoint of ledgercomm-parse binary."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest="command"
    )
    # file subparser
    parser_file = subparsers.add_parser(
        "file",
        help="send APDUs from file"
    )
    parser_file.add_argument(
        "filepath",
        help="path of the file within APDUs"
    )
    # stdin subparser
    _ = subparsers.add_parser(
        "stdin",
        help="send APDUs from stdin"
    )
    # stdin subparser
    parser_log = subparsers.add_parser(
        "log",
        help="send APDUs from Ledger Live log file"
    )
    parser_log.add_argument(
        "filepath",
        help="path of the Ledger Live log file within APDUs"
    )
    # args for main parser
    parser.add_argument(
        "--hid",
        help="Use HID instead of TCP client",
        action="store_true"
    )
    parser.add_argument(
        "--server",
        help="IP server of the TCP client (default: 127.0.0.1)",
        default="127.0.0.1"
    )
    parser.add_argument(
        "--port",
        help="Port of the TCP client (default: 9999)",
        default=9999
    )
    parser.add_argument(
        "--startswith",
        help="Only send APDUs which starts with STARTSWITH (default: None)",
        default=None
    )

    args = parser.parse_args()

    transport = (Transport(interface="hid", debug=True) if args.hid
                 else Transport(interface="tcp",
                                server=args.server,
                                port=args.port,
                                debug=True))

    if args.command == "file":
        filepath: Path = Path(args.filepath)

        for apdu in parse_file(filepath, args.startswith):  # type: str
            if apdu:
                transport.exchange_raw(re.sub(r"[^a-fA-F0-9]", "", apdu))

    if args.command == "stdin":
        apdu: str = input()

        if args.startswith:
            apdu = apdu.replace(args.startswith, "").strip()

        if apdu:
            transport.exchange_raw(re.sub(r"[^a-fA-F0-9]", "", apdu))

    if args.command == "log":
        # TODO: implement Ledger Live log parser
        raise NotImplementedError("Ledger Live log parser is not yet available!")

    transport.close()

    return 0


if __name__ == "__main__":
    main()
