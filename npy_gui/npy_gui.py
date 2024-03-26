"""The graphical user interface for the ledgeradd programm."""

from general.ledgerparse import Transaction
from general import ledgeradd
from general.settings import Settings
from npy_gui.npy_afaform import AfaCheckForm
from npy_gui.npy_afaform import AfaTypeChooseForm
from npy_gui.npy_afaform import AfaPostingChooseForm
from npy_gui.npy_presetform import PresetForm
from npy_gui.npy_transactionform import TransactionForm
from npy_gui.npy_transactioncheckform import TransactionCheckForm
from npy_gui.npy_settingsform import SettingsForm
import npyscreen


class LedgeraddApplication(npyscreen.NPSAppManaged):
    """The main application object."""

    def __init__(self, settings, presets, *args, **kwargs):
        """Initialize the class."""
        super(LedgeraddApplication, self).__init__(*args, **kwargs)

        # get settings and presets
        self.S = settings
        self.P = presets

        # get presets
        # self.P = Preset(data_path=self.S.data_path)

        # set global temp variables
        self.tmpTrans = Transaction()
        self.tmpTransC = Transaction()  # copy of the trans
        self.tmpTrans_new = True
        self.tmpPosting = None
        self.tmpTransList = []
        self.tmpJournals = None

        # history for added transactions during runtime of the programm
        self.History = ''

    def gen_tmptrans(self):
        """Generate tmpTrans."""
        self.tmpTrans = ledgeradd.default_transaction(
            settings=self.S
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
        self.addForm(
            'Settings',
            SettingsForm,
            name='Ledgeradd > Settings'
        )

        # afa feature
        self.addForm(
            'AfaCheck',
            AfaCheckForm,
            name='Ledgeradd > Afa feature check'
        )
        self.addForm(
            'AfaPostingChoose',
            AfaPostingChooseForm,
            name='Choose posting for tax depreciation (ok = cancel)'
        )
        self.addForm(
            'AfaTypeChoose',
            AfaTypeChooseForm,
            name='Choose type for tax depreciation (ok = cancel)'
        )

        # preset form
        self.addForm(
            'Presets',
            PresetForm,
            name='Ledgeradd > Presets'
        )
