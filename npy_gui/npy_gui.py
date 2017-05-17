"""The graphical user interface for the ledgeradd programm."""

from general.ledgerparse import Transaction
from general.settings import Settings
from npy_gui.npy_transactionform import TransactionForm
from npy_gui.npy_settingsform import SettingsForm
import npyscreen


class LedgeraddApplication(npyscreen.NPSAppManaged):
    """The main application object."""

    def onStart(self):
        """Create all the forms and variables, which are needed."""
        # get global variables for the app
        self.S = Settings()
        # self.P = Preset(data_path=self.S.data_path)

        # set global temp variables
        self.tmpTrans = Transaction()

        # create the forms
        self.addForm(
            'MAIN',
            TransactionForm,
            name='Ledgeradd'
        )
        self.addForm(
            'Settings',
            SettingsForm,
            name='Ledgeradd > Settings'
        )
