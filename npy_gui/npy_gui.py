"""The graphical user interface for the ledgeradd programm."""

from general.ledgerparse import Transaction
from npy_gui.npy_transactionform import TransactionForm
from npy_gui.npy_transactioncheckform import TransactionCheckForm
from npy_gui.npy_settingsform import SettingsForm
import npyscreen


class LedgeraddApplication(npyscreen.NPSAppManaged):
    """The main application object."""

    def __init__(self, settings, *args, **kwargs):
        """Initialize the class."""
        super(LedgeraddApplication, self).__init__(*args, **kwargs)

        # get settings
        self.S = settings

        # get presets
        # self.P = Preset(data_path=self.S.data_path)

        # set global temp variables
        self.tmpTrans = Transaction()
        self.tmpTransC = Transaction()  # copy of the trans
        self.tmpTrans_new = True

        # history for added transactions during runtime of the programm
        self.History = ''

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
            account=self.S.def_account_a,
            no_amount=True
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_b,
            no_amount=True
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_c,
            no_amount=True
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_d,
            no_amount=True
        )

        self.tmpTrans.add_posting(
            account=self.S.def_account_e,
            no_amount=True
        )

        self.tmpTrans_new = False

    def onStart(self):
        """Create all the forms and variables, which are needed."""
        # create the forms
        self.addForm(
            'MAIN',
            TransactionForm,
            name='Ledgeradd'
        )
        self.addForm(
            'TransactionCheck',
            TransactionCheckForm,
            name='Ledgeradd > Check',
            color='WARNING'
        )

        # settings name
        if self.S._got_arguments:
            settings_title = (
                'Ledgeradd > Settings (arguments altered settigns - cannot save!'
            )
            settings_color = 'DANGER'
        else:
            settings_title = 'Ledgeradd > Settings'
            settings_color = 'FORMDEFAULT'
        self.addForm(
            'Settings',
            SettingsForm,
            name=settings_title,
            color=settings_color
        )
