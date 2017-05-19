"""
A simple programm for adding ledger transactions to the ledger-cli formatted journal.

You can add manually or save and load presets.

Author: Manuel Senfft (www.tagirijus.de)
"""

import argparse
from npy_gui import npy_gui


def main():
    """Run the programm with the npyscreen GUI."""
    args = argparse.ArgumentParser(
        description=(
            'Programm for adding ledger transactions to a ledger journal.'
        )
    )

    args.add_argument(
        'file',
        nargs='?',
        default=None,
        help='ledger journal'
    )

    # args.add_argument(
    #     '-s',
    #     '--short',
    #     type=int,
    #     default=12345,
    #     help='Simple integer argument'
    # )

    args = args.parse_args()

    app = npy_gui.LedgeraddApplication(arguments=args)
    app.run()

if __name__ == '__main__':
    main()
