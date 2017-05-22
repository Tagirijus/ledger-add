"""The graphical user interface for the ledgeradd programm."""

from general.ledgerparse import Transaction
from general import ledgeradd
from general.settings import Settings
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
        self.tmp_first = True
        self.tmpTrans = Transaction()
        self.tmpTransC = Transaction()  # copy of the trans
        self.tmpTrans_new = True

        # history for added transactions during runtime of the programm
        self.History = ''

    def gen_tmptrans(self):
        """Generate tmpTrans."""
        # reload settings, if it's not the first time generating the trans
        if not self.tmp_first:
            self.S = Settings(ignore_arguments=True)

        # generate the trans and set flag "new"
        self.tmpTrans = ledgeradd.default_transaction(
            settings=self.S
        )

        self.tmpTrans_new = False

        # loaded after startup. after this the settings default will be get
        self.tmp_first = False

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
        self.addForm(
            'Settings',
            SettingsForm,
            name='Ledgeradd > Settings'
        )
