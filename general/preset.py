"""Class for preset management."""

from general.ledgerparse import Transaction
import json
import os
import shutil


class Preset(object):
    """Preset class for loading and saving presets."""

    def __init__(
        self,
        data_path=None,
        trans_dir='/presets_transaction',
        trans_list=None,
    ):
        """Initialize the class."""
        self.data_path = data_path

        is_dir = os.path.isdir(str(self.data_path))
        if not is_dir:
            raise IOError

        self.trans_dir = trans_dir
        self.trans_list = (self.load_trans_list_from_file() if trans_list is None
                           else trans_list)

    def save_trans_list_to_file(self):
        """Save transactin preset list to file."""
        for name in [t['name'] for t in self.trans_list]:
            self.save_trans_to_file(name=name)

    def load_trans_list_from_file(self):
        """Load the transs from file and return trans_list."""
        path = self.data_path + self.trans_dir

        # check if the data_path/trans_presets directory exists and cancel otherwise
        if not os.path.isdir(str(path)):
            return []

        # cycle through the files and append them converted from json to the list
        out = []
        for file in sorted(os.listdir(path)):
            if file.endswith('.latrans'):
                # load the file
                f = open(path + '/' + file, 'r')
                load = f.read()
                f.close()

                # convert file content to transactin preset and append it
                out.append(json.loads(load))

        return out

    def add_trans(self, name=None, info=None, transaction=None):
        """Append the transaction to the presets."""
        name = str(name)
        info = str(info)
        is_trans = type(transaction) is Transaction
        already_exists = name in [t['name'] for t in self.trans_list]

        if not is_trans or already_exists:
            return False

        self.trans_list.append(
            {
                'info': info,
                'name': name,
                'transaction': transaction.to_str()
            }
        )

        # also save the file immediately
        self.save_trans_to_file(name=name)

        return True

    def get_trans(self, name=None):
        """Return transactin preset (dict) by name."""
        name = str(name)
        for t in self.trans_list:
            if name == t['name']:
                return t

        return False

    def save_trans_to_file(self, name=None):
        """Save single transaction preset to file."""
        name = str(name)
        name_exists = False

        # get transaction preset by name
        for t in self.trans_list:
            if name == t['name']:
                name_exists = True
                trans_preset = t
                break

        if not name_exists:
            return False

        path = self.data_path + self.trans_dir

        # create dir if it does not exist
        is_dir = os.path.isdir(str(path))
        is_file = os.path.isfile(str(path))
        if not is_dir and not is_file:
            os.mkdir(path)

        # generate filenames
        filename = path + '/' + self.us(name) + '.latrans'
        filename_bu = path + '/' + self.us(name) + '.latrans_bu'

        # if it exists, delete
        if os.path.isfile(filename):
            shutil.copy2(filename, filename_bu)

        # write the file
        f = open(filename, 'w')
        f.write(json.dumps(trans_preset, indent=2))
        f.close()

    def delete_trans_file(self, name=None):
        """Delete single transaction preset file."""
        name = str(name)
        name_exists = name in [t['name'] for t in self.trans_list]

        if not name_exists:
            return False

        path = self.data_path + self.trans_dir

        # generate filenames
        filename = path + '/' + self.us(name) + '.latrans'

        # if it exists, delete
        if os.path.isfile(filename):
            os.remove(filename)
            return True
        else:
            return False

    def remove_trans(self, name=None):
        """Remove transaction preset, if it exists."""
        name = str(name)
        name_exists = False

        # get its index and check if it exists
        for i, t in enumerate(self.trans_list):
            if name == t['name']:
                index = i
                name_exists = True
                break

        if not name_exists:
            return False

        # try to remove the transaction preset
        try:
            self.delete_trans_file(name=name)
            self.trans_list.pop(index)
            return True
        except Exception:
            return False

    def us(self, string=''):
        """Return string with underscores instead of whitespace."""
        return string.replace(' ', '_')
