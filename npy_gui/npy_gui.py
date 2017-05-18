"""The graphical user interface for the ledgeradd programm."""

from datetime import datetime
from general.ledgerparse import Transaction
from general.settings import Settings
from npy_gui.npy_transactionform import TransactionForm
from npy_gui.npy_transactioncheckform import TransactionCheckForm
from npy_gui.npy_settingsform import SettingsForm
import npyscreen


class LedgeraddApplication(npyscreen.NPSAppManaged):
    """The main application object."""

    def gen_tmptrans(self):
        """Generate tmpTrans."""
        self.tmpTrans = Transaction(
            decimal_sep=self.S.dec_separator,
            date_sep=self.S.date_separator,
            state=self.S.def_state,
            code=self.S.def_code,
            payee=self.S.def_payee
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_a
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_b
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_c
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_d
        )

        self.tmpTrans_new = False

    def onStart(self):
        """Create all the forms and variables, which are needed."""
        # get global variables for the app
        self.S = Settings()
        # self.P = Preset(data_path=self.S.data_path)

        # set global temp variables
        self.tmpTrans = Transaction()
        self.tmpTrans_new = True

        # create the forms
        self.addForm(
            'MAIN',
            TransactionForm,
            name='Ledgeradd'
        )
        self.addForm(
            'TransactionCheck',
            TransactionCheckForm,
            name='Ledgeradd > Check'
        )
        self.addForm(
            'Settings',
            SettingsForm,
            name='Ledgeradd > Settings'
        )
