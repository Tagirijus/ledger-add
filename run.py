"""
A simple programm for adding ledger transactions to the ledger-cli formatted journal.

You can add manually or save and load presets.

Author: Manuel Senfft (www.tagirijus.de)
"""

from npy_gui import npy_gui


def main():
    """Run the programm with the npyscreen GUI."""
    app = npy_gui.LedgeraddApplication()
    app.run()

if __name__ == '__main__':
    main()
