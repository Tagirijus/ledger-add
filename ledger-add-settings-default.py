# coding=utf-8

# configurarion

# !!! ATTENTION !!!
#
# The following option 'modify_ledger_file' will not only append new data to your file,
# but also rewrite the file with sorted and/or modified entries. It is only useful, if
# you like to add older entries afterwards, while keeping the corrrect order of the entries
# in the journal-file. And it is used for the cleared/pending transaction feature!
# If there are bugs in the code, this function could totally destroy your original
# ledger-journal file. Chose 'False', if you like to be more save. Otherwise chose
# 'True' and feel free to trust my non-professional development skills. (-;
#
# !!! ATTENTION !!!

modify_ledger_file = True


# some default values

default_transaction_name = 'Einkaufen'
default_account_one_name = 'in:{name}'			# {name} = replaced with name of transaction
default_commodity = '€'
ask_commodity = False

# info_text and color variables - and boolean for switching between color modes

info_text	 =  'Infotext line 1\n'
info_text	 += 'Infotext line 2\n'

colorize = True

WHITE = '\033[97m'
PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
BOLD = '\033[1m'
DIM = '\033[2m'
GREY = '\033[90m'
UNDERLINE = '\033[4m'

# customize the colors here !!!

# normal text
CL_TXT = PURPLE if colorize else ''
# info, error and warning text
CL_INF = BOLD + RED if colorize else ''
# default values
CL_DEF = YELLOW if colorize else ''
# dimmed output
CL_DIM = GREY if colorize else ''
# final output
CL_OUT = BOLD + YELLOW if colorize else ''

# don't change this- it's the ending string for the coloring strings
CL_E = '\033[0m' if colorize else ''