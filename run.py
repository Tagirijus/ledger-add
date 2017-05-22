"""
A simple programm for adding ledger transactions to the ledger-cli formatted journal.

You can add manually or save and load presets.

Author: Manuel Senfft (www.tagirijus.de)
"""

from general.settings import Settings
from npy_gui import npy_gui


def main():
    """Run the programm."""
    # load the settings
    settings = Settings()

    # start the GUI
    if not settings.args.nogui:
        app = npy_gui.LedgeraddApplication(settings=settings)
        app.run()

    # start the non-GUI version
    pass

if __name__ == '__main__':
    main()
