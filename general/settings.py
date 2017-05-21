"""The class holding all the settings."""

import argparse
from datetime import datetime
from decimal import Decimal
import json
import os


class Settings(object):
    """Settings class."""

    def __init__(
        self,
        data_path=None,
        ledger_path=None,
        def_state=None,
        def_code=None,
        def_payee=None,
        def_commodity=None,
        def_account_a=None,
        def_account_b=None,
        def_account_c=None,
        def_account_d=None,
        def_account_e=None,
        dec_separator=None,
        date_separator=None,
        ledger_file=None,
        split_years_to_files=None,
        afa_threshold_amount=None,
        afa_def_account=None,
        afa_table=None
    ):
        """Initialize the class and hard code defaults, if no file is given."""
        self.args = argparse.ArgumentParser(
            description=(
                'Programm for adding ledger transactions to a ledger journal.'
            )
        )

        self.args.add_argument(
            'file',
            nargs='?',
            default=None,
            help=(
                'ledger journal - if set, split years feature is set to false by default!'
            )
        )

        self.args.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            help='disables the GUI'
        )

        self.args.add_argument(
            '-s',
            '--split',
            action='store_true',
            help='enables split years to files'
        )

        self.args = self.args.parse_args()

        self._got_arguments = False

        self.BASE_PATH = os.path.dirname(os.path.realpath(__file__))[
            :os.path.dirname(os.path.realpath(__file__)).rfind('/')
        ]

        # check if data_path.flsettings exist in the base path of the script
        if os.path.isfile(self.BASE_PATH + '/data_path.lasettings'):
            f = open(self.BASE_PATH + '/data_path.lasettings', 'r')
            data_path = f.read().strip()
            f.close()

        # settings and programm
        self.data_path = (os.path.expanduser('~') + '/.tagirijus_ledgeradd'
                          if data_path is None else data_path)

        # generate ledgeradd dir under ~/.tagirijus_ledgeradd, if it does not exist
        self.generate_data_path()

        # ledger path
        ledger_path_default = (
            os.environ['LEDGER_FILE_PATH'] if 'LEDGER_FILE_PATH' in os.environ
            else self.data_path + '/ledger_journals'
        )
        self.ledger_path = (
            ledger_path_default
            if ledger_path is None else ledger_path
        )

        # generate ledger path, if it does not exist
        self.generate_ledger_path()

        # initialize the attributes

        # default values
        self.def_state = '*' if def_state is None else def_state
        self.def_code = '' if def_code is None else def_code
        self.def_payee = '' if def_payee is None else def_payee
        self.def_commodity = '€' if def_commodity is None else def_commodity
        self.def_account_a = '' if def_account_a is None else def_account_a
        self.def_account_b = '' if def_account_b is None else def_account_b
        self.def_account_c = '' if def_account_c is None else def_account_c
        self.def_account_d = '' if def_account_d is None else def_account_d
        self.def_account_e = '' if def_account_e is None else def_account_e

        # formatting
        self.dec_separator = ',' if dec_separator is None else dec_separator
        self.date_separator = '-' if date_separator is None else date_separator

        # file handling
        ledger_file_default = (
            os.environ['LEDGER_FILE'] if 'LEDGER_FILE' in os.environ
            else 'ledgeradd_ledger.journal'
        )
        self.ledger_file = (
            ledger_file_default if ledger_file is None else ledger_file
        )
        self.set_split_years_to_files(
            True if split_years_to_files is None else split_years_to_files
        )

        # afa feature
        self._afa_threshold_amount = Decimal('487.90')
        self.set_afa_threshold_amount(afa_threshold_amount)
        self.afa_def_account = 'afa' if afa_def_account is None else afa_def_account
        self._afa_table = []
        self.set_afa_table(afa_table)

        # try to load settings from self.data_path/ledgeradd.settings afterwards
        self.load_settings_from_file()

        # alter it from arguments
        self._set_from_arguments()

    def _set_from_arguments(self):
        """Feed own attributes from arguments."""
        # a file is given in the arguments
        if self.args.file is not None:
            # so set this file and also set the split_years... to False
            self.ledger_file = self.args.file
            self.ledger_path = os.path.dirname(
                os.path.abspath(self.args.file)
            )
            self._split_years_to_files = False

            # self.args altered the settings. this will disable saving the settings
            self._got_arguments = True

        if self.args.split:
            self._split_years_to_files = True

            # arguments altered the settings. this will disable saving the settings
            self._got_arguments = True

    @property
    def ledger_file(self):
        """Return ledger_file."""
        return self._ledger_file

    @ledger_file.setter
    def ledger_file(self, value):
        """Set ledger_file."""
        self._ledger_file = value + '.journal' if '.' not in value else value

    def set_split_years_to_files(self, value):
        """Set split_years_to_files."""
        self._split_years_to_files = bool(value)

    def get_split_years_to_files(self):
        """Get split_years_to_files."""
        return self._split_years_to_files

    def set_afa_threshold_amount(self, value):
        """Set afa_threshold_amount."""
        try:
            self._afa_threshold_amount = Decimal(str(value))
        except Exception:
            pass

    def get_afa_threshold_amount(self):
        """Get afa_threshold_amount."""
        return self._afa_threshold_amount

    def set_afa_table(self, value):
        """Set afa_table."""
        try:
            self._afa_table = list(value)
        except Exception:
            pass

    def get_afa_table(self):
        """Get afa_table."""
        return self._afa_table

    def add_afa_table(self, name=None, account=None, years=None):
        """Add afa_table entry."""
        # try to convert years to int
        try:
            years = int(years)
        except Exception:
            # did not work, return False
            return False

        # add the new afa_table entry
        self._afa_table.append(
            {
                'name': name,
                'account': account,
                'years': years
            }
        )

        return True

    def del_afa_table(self, index=None):
        """Remove the list entry with the given index."""
        if type(index) is not int:
            return False

        if index > len(self._afa_table) - 1:
            return False

        self._afa_table.pop(index)
        return True

    def gen_ledger_filename(
        self,
        absolute=False,
        year=None,
        path_only=False
    ):
        """Generate ledger filename."""
        # get settings ledger_path
        path = self.ledger_path + '/' if (absolute or path_only) else ''

        # return path only, if the argument for it is True
        if path_only:
            return path

        if type(year) is not int:
            year = datetime.now().year

        # generate filename for specific year, if this feature is enabled
        if self._split_years_to_files:
            return path + self.ledger_file.replace('.', '_{}.'.format(year))
        else:
            return path + self.ledger_file

    def to_json(self, indent=2, ensure_ascii=False):
        """Convert settings data to json format."""
        out = {}

        # fetch all setting variables
        out['data_path'] = self.data_path
        out['ledger_path'] = self.ledger_path
        out['def_state'] = self.def_state
        out['def_code'] = self.def_code
        out['def_payee'] = self.def_payee
        out['def_commodity'] = self.def_commodity
        out['def_account_a'] = self.def_account_a
        out['def_account_b'] = self.def_account_b
        out['def_account_c'] = self.def_account_c
        out['def_account_d'] = self.def_account_d
        out['def_account_e'] = self.def_account_e
        out['dec_separator'] = self.dec_separator
        out['date_separator'] = self.date_separator
        out['ledger_file'] = self.ledger_file
        out['split_years_to_files'] = self._split_years_to_files
        out['afa_threshold_amount'] = float(self._afa_threshold_amount)
        out['afa_def_account'] = self.afa_def_account
        out['afa_table'] = self._afa_table

        # return the json
        return json.dumps(
            out,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=True
        )

    def feed_json(self, js=None):
        """Feed settings variables from json string."""
        if js is None:
            return

        # get js as dict
        try:
            js = json.loads(js)
        except Exception:
            # do not load it
            return

        # feed settings variables
        if 'data_path' in js.keys():
            self.data_path = js['data_path']

        if 'ledger_path' in js.keys():
            self.ledger_path = js['ledger_path']

        if 'def_state' in js.keys():
            self.def_state = js['def_state']

        if 'def_code' in js.keys():
            self.def_code = js['def_code']

        if 'def_payee' in js.keys():
            self.def_payee = js['def_payee']

        if 'def_commodity' in js.keys():
            self.def_commodity = js['def_commodity']

        if 'def_account_a' in js.keys():
            self.def_account_a = js['def_account_a']

        if 'def_account_b' in js.keys():
            self.def_account_b = js['def_account_b']

        if 'def_account_c' in js.keys():
            self.def_account_c = js['def_account_c']

        if 'def_account_d' in js.keys():
            self.def_account_d = js['def_account_d']

        if 'def_account_e' in js.keys():
            self.def_account_e = js['def_account_e']

        if 'dec_separator' in js.keys():
            self.dec_separator = js['dec_separator']

        if 'date_separator' in js.keys():
            self.date_separator = js['date_separator']

        if 'ledger_file' in js.keys():
            self.ledger_file = js['ledger_file']

        if 'split_years_to_files' in js.keys():
            self.set_split_years_to_files(js['split_years_to_files'])

        if 'afa_threshold_amount' in js.keys():
            self.set_afa_threshold_amount(js['afa_threshold_amount'])

        if 'afa_def_account' in js.keys():
            self.afa_def_account = js['afa_def_account']

        if 'afa_table' in js.keys():
            self.set_afa_table(js['afa_table'])

    def gen_abs_path_to_settings_file(self):
        """Generate the absolut path to the settings file."""
        return self.data_path + '/ledgeradd.settings'

    def generate_data_path(self):
        """Check if data_path exists or create dir."""
        is_dir = os.path.isdir(str(self.data_path))
        is_file = os.path.isfile(str(self.data_path))

        # raise error, if it is a file
        if is_file:
            raise IOError

        # create if it does not exist
        if not is_dir:
            os.mkdir(self.data_path)

    def generate_ledger_path(self):
        """Check if ledger_path exists or create dir."""
        is_dir = os.path.isdir(str(self.ledger_path))
        is_file = os.path.isfile(str(self.ledger_path))

        # raise error, if it is a file
        if is_file:
            raise IOError

        # create if it does not exist
        if not is_dir:
            os.mkdir(self.ledger_path)

    def save_settings_to_file(self):
        """Save the settings to file in data_path."""
        # do not save, if arguments altered the settings
        if self._got_arguments:
            return

        # generate data_path if it does not exist
        self.generate_data_path()

        # save the path to BASE_PATH/data_path.flsettings
        f = open(self.BASE_PATH + '/data_path.flsettings', 'w')
        f.write(self.data_path)
        f.close()

        # save settings to the data_path
        f = open(self.gen_abs_path_to_settings_file(), 'w')
        f.write(self.to_json())
        f.close()

    def load_settings_from_file(self):
        """Load the settings from file in data_path."""
        # check if the file exists
        if os.path.isfile(self.gen_abs_path_to_settings_file()):
            # load content from file
            f = open(self.gen_abs_path_to_settings_file(), 'r')
            loaded = f.read().strip()
            f.close()

            # and feed own variables with it
            self.feed_json(loaded)
