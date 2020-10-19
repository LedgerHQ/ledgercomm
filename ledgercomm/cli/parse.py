"""ledgercomm.cli.parse module."""

import argparse
from pathlib import Path
import re
from typing import Iterator, Optional

from ledgercomm import RawTransport


def parse_file(filepath: Path, condition: Optional[str]) -> Iterator[str]:
    """Filter with `condition` and yield line of `filepath`."""
    with open(filepath, "r") as f:
        for line in f:
            if condition and line.startswith(condition):
                yield line.replace(condition, "")
            else:
                yield line


def main():
    """Entrypoint of ledgercomm-parse binary."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_path",
        help="path of the file within APDUs"
    )
    parser.add_argument(
        "--hid",
        help="Use HID instead of TCP client",
        action="store_true"
    )
    parser.add_argument(
        "--server",
        help="IP server of the TCP client",
        default="127.0.0.1"
    )
    parser.add_argument(
        "--port",
        help="Port of the TCP client",
        default=9999
    )
    parser.add_argument(
        "--condition",
        help="Only send APDUs on line starting with condition"
    )

    args = parser.parse_args()

    filepath: Path = Path(args.file_path)

    transport = (RawTransport(hid=True, debug=True) if args.hid
                 else RawTransport(server=args.server, port=args.port, debug=True))

    for raw_apdus in parse_file(filepath, args.condition):  # type: str
        transport.exchange(re.sub(r"[^a-fA-F0-9]", "", raw_apdus))

    return 0


if __name__ == "__main__":
    main()
