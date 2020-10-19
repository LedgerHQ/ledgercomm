"""setup module."""

from pathlib import Path
import re
from setuptools import setup, find_packages

name = "ledgercomm"

version = re.search(
    r"""(?x)
    __version__
    \s=\s
    \"
    (?P<number>.*)
    \"
    """,
    Path(f"{name}/__init__.py").read_text()
)

setup(
    name=name,
    version=version["number"],
    description="Library to communicate with Nano S/X and Speculos",
    long_description=Path("README.md").read_text(),
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "hid": ["hidapi>=0.9.0.post3"],
        "repl": ["ipython>=7.17.0"]
    },
    entry_points={
        "console_scripts": [
            "ledgercomm-repl = ledgercomm.cli.repl:main",
            "ledgercomm-parse = ledgercomm.cli.parse:main"
        ],
    },
    zip_safe=True
)
