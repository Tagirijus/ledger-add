"""Module holding the general functions."""

import os
import shlex


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


def acc_list_to_multiline(accounts=None):
    """Convert account list [name, amount, comments] to multiline."""
    if type(accounts) is not list:
        return []

    out = []

    # cycle through the accounts
    for a in accounts:
        acc_amt = []
        cms = []

        # get account and amount or comment
        for x in a:
            if ';' not in x:
                # add it in quotes if there are more than two following whitespaces
                if '  ' in x:
                    x = '"{}"'.format(x)
                acc_amt += [x]
            else:
                cms += [x]

        # now generate the lines

        # first line has account and maybe amount
        out += [' '.join(acc_amt)]

        # next lines have all the comments
        for x in cms:
            out += [x]

    return out


def multiline_to_acc_list(multi=None):
    """Return an account list like [name, amount, comments] from text."""
    if type(multi) is not list:
        return []

    out = []

    # cycle through the lines
    for l in multi:

        # no comment, add account and amount
        if ';' not in l:
            out += [shlex.split(l)[:2]]

        # comment, add it without the ; to the last added account and amount
        else:
            # but there must be more than 0 entries already
            if len(out) > 0:
                out[len(out) - 1] += [l]

    return out
