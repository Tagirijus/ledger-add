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


def multiline_to_acc_list(multi=None, dec_sep=','):
    """Return an account list like [name, amount, comments] from text."""
    if type(multi) is not list:
        return []

    out = []

    # cycle through the lines
    for l in multi:

        # no comment, add account and amount
        if ';' not in l:
            # get the line like parameters
            strings = shlex.split(l)

            # check if last entry can be converted to a number
            try:
                amt_exists = type(float(strings[-1].replace(dec_sep, '.'))) is float
            except Exception:
                amt_exists = False

            # entry is with amount on last position
            if amt_exists:
                # get all but the last entry as the account name
                acc = ' '.join(strings[:-1])

                # get last as the amount
                amt = strings[-1]

                out += [[acc, amt]]

            # entry is without amount
            else:
                # get the account name
                acc = ' '.join(strings)

                out += [[acc]]

        # comment, add it without the ; to the last added account and amount
        else:
            # but there must be more than 0 entries already
            if len(out) > 0:
                out[len(out) - 1] += [l]

    return out


def move_list_entry(lis=None, index=None, direction=None):
    """Move an list entry with index in lis up/down."""
    one_not_set = lis is None or index is None or direction is None
    out_of_range = index >= len(lis)

    # cancel, if one argument is not set or offer_index is out of range
    if one_not_set or out_of_range:
        return

    # calculate new index: move up (direction == 1) or down (direction == -1)
    new_index = index + direction

    # put at beginning, if it's at the end and it's moved up
    new_index = 0 if new_index >= len(lis) else new_index

    # put at the end, if it's at the beginning and moved down
    new_index = len(lis) - 1 if new_index < 0 else new_index

    # move it!
    lis.insert(new_index, lis.pop(index))

    # return new index
    return new_index
