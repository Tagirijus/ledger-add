"""Module holding the general functions."""

import os


def can_be_dir(string):
    """
    Check if the given string could be a creatable dir or exists.

    The function checks if the string already exists and is a directory.
    It also tries to create a new folder in this folder to check, if
    the neccessary permission is granted.
    """
    try:
        # check if it already exists
        if os.path.exists(string):
            if os.path.isdir(string):
                # it already exists and is a dir
                try:
                    # try to create a dir inside it to check permission
                    os.mkdir(string + '/TAGIRIJUS_LEDGERADD_CHECK')
                    os.rmdir(string + '/TAGIRIJUS_LEDGERADD_CHECK')
                    # worked!
                    return True
                except Exception:
                    # no permission probably
                    return False
            else:
                # it already exists and is probably a file
                return False
        else:
            # it does not exist, try to create it
            os.mkdir(string)
            os.rmdir(string)
            return True
    except Exception:
        # no permission maybe
        return False
