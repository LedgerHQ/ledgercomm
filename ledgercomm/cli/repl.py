"""ledgercomm.cli.repl module."""

try:
    import IPython
except ImportError:
    IPython = None

from ledgercomm import Transport


def main():
    """Entrypoint of ledgercomm-repl binary."""
    if IPython is None:
        raise ImportError("IPython is not installed, try: "
                          "'pip install ledgercomm[all]'")

    scope_vars = {"Transport": Transport}
    print("Welcome to ledgercomm REPL!")
    IPython.start_ipython(argv=[], user_ns=scope_vars)

    # TODO: configure interface and parse all strings to sent them as raw APDUs

    return 0


if __name__ == "__main__":
    main()
