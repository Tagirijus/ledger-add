"""
A simple programm for adding ledger transactions to the ledger-cli formatted journal.

You can add manually or save and load presets.

Author: Manuel Senfft (www.tagirijus.de)
"""

from general import ledgeradd
from general.settings import Settings
from general.preset import Preset
from npy_gui import npy_gui


def main():
    """Run the programm."""
    # load the settings
    settings = Settings()
    presets = Preset(data_path=settings.data_path)

    # start the GUI
    if not settings.args.nogui:
        app = npy_gui.LedgeraddApplication(settings=settings, presets=presets)
        app.run()

    # start the non-GUI version - afa feature
    elif settings.args.nogui and settings.args.afa_feature:
        ledgeradd.non_gui_afa_feature(settings=settings)

    # just start the non-GUI version
    else:
        ledgeradd.non_gui_application(settings=settings, presets=presets)

if __name__ == '__main__':
    main()
