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
    url="https://github.com/LedgerHQ/ledgercomm",
    python_requires=">=3.8.0",
    description="Library to communicate with Ledger Nano S/X and Speculos",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    extras_require={
        "hid": ["hidapi>=0.9.0.post3"]
    },
    entry_points={
        "console_scripts": [
            "ledgercomm-send = ledgercomm.cli.send:main"
        ],
    },
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX"
    ],
    author="grydz",
    author_email="hello@ledger.fr"
)
