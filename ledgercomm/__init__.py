"""ledgercomm module."""

from ledgercomm.transport import Transport

try:
    from ledgercomm.__version__ import __version__  # noqa
except ImportError:
    __version__ = "unknown version"  # noqa

__all__ = ["Transport"]
