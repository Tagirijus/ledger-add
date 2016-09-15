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


# internal aliases

aliases = {
	'a': 'assets',
	'e': 'expenses'
	}

# some default values

default_transaction_name = 'Einkaufen'
default_account_one_name = 'in:{name}'			# {name} = replaced with name of transaction
default_receiving_account = 'Assets'
invoice_transaction_add = ' [paid]'
default_commodity = '€'
ask_commodity = False
ask_account_comment = False
dec_sep = ',' # decimal seperator
preset_wildcard = '[*]' # use this string in a preset, so that you will be ask to enter only this position later, when chosing the preset

# info_text and color variables - and boolean for switching between color modes

info_text	 =  'Infotext line 1\n'
info_text	 += 'Infotext line 2\n'

# date and file stuff

split_journal_into_years = True
default_filename = 'ledger_{YEAR}.journal'
default_ledger_path = '/home/USER/ledger'
date_sep	= '-'			# only use '/' or '-'
date_format	= '%Y' + date_sep + '%m' + date_sep + '%d'	# don't change this !

##
# afa feature

# if afa_accounts array is empty, the afa feature will ask for evey account if it's afa. you can disable the afa_feature by adding 'disabled' to the array (it will ignore cases)
afa_accounts	= ['disabled']

# german threshold. above this the expense can only reduce tax for X years (according to the afa table). the value is meant to be 410 taxfree and 487,9 with 19% taxes
afa_threshold_amount		= 487.9
afa_per_day_or_month		= 'month' # month | day

# afa account
afa_def_account = 'afa'
afanon_def_account = 'afanon'
afa_append_comment = False

# some entries from german afa table for reducing tax over X years
# it is used like this:  afa_table[ WHAT_THING ] = (YEARS, ACCOUNT_STRING)
afa_table		= {
	'Mikrofon': (5, '[ACCOUNT]:Equipment'),
	'Mikrofon (kabellos)': (3, '[ACCOUNT]:Equipment'),
	'Computer': (3, '[ACCOUNT]:Computer'),
	'Software': (3, '[ACCOUNT]:Software'),
	'Werbungskosten': (1, '[ACCOUNT]:Werbungskosten'),
	'Fahrtkosten': (1, '[ACCOUNT]:Fahrtkosten'),
	'Telefonie': (1, '[ACCOUNT]:Telefonie'),
	'Miete': (1, '[ACCOUNT]:Miete')
	}

# afa feature
##

# color stuff

colorize = True

WHITE = '\033[97m'
PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
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
# account or transaction for afa
CL_ACC = CYAN if colorize else ''
# final output
CL_OUT = BOLD + YELLOW if colorize else ''

# don't change this- it's the ending string for the coloring strings
CL_E = '\033[0m' if colorize else ''