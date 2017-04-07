# coding=utf-8

#
# Programm for adding simple ledger transactions.
# There's a preset system: Press 'p' to chose a preset and save one in the final prompt.
#

import os, sys, datetime, imp, ledgerparse


### ### ###
### ### ### load configurarion file for variables
### ### ###

# !!!!! SET YOUR INDIVIDUAL SETTINGS FILE HERE
# !!!!! IT MUST BE SET UP LIKE THE 'ledger-add-settings-default.py' FILE
####
###
#

SETTINGS_FILE = 'ledger-add-settings.py'

#
###
####
# !!!!!
# !!!!!

# get the actual path to the python script
path_to_project = os.path.dirname(os.path.realpath(__file__))


# check if user set an individual settings file, or load default otherwise

if os.path.isfile(path_to_project + '/' + SETTINGS_FILE):
	print 'Loading configuration PERSONAL'
	configuration = imp.load_source('ledger-add-settings', path_to_project + '/' + SETTINGS_FILE)
	configuration_def = imp.load_source('ledger-add-settings-default', path_to_project + '/ledger-add-settings-default.py')
else:
	if os.path.isfile(path_to_project + '/ledger-add-settings-default.py'):
		configuration = imp.load_source('ledger-add-settings-default', path_to_project + '/ledger-add-settings-default.py')
	else:
		print 'No settings file found.'
		exit()



# configuartion function

def config(att):
	if hasattr(configuration, att):
		return getattr(configuration, att)
	else:
		print 'Please update your personal settings file:', att
		return getattr(configuration_def, att)

def journal_file(name=None, year=None):
	# get automatic year or user input
	if year == None:
		year = datetime.datetime.now().strftime('%Y')
	else:
		year = str(year)

	# generate automatic filename
	if name == None:
		name = default_filename.replace('{YEAR}', year)

	# LEDGER_FILE_PATH is set
	if 'LEDGER_FILE_PATH' in os.environ:
		return os.environ['LEDGER_FILE_PATH'] + '/' + name

	# it is not set, use teh path from the settings file
	elif os.path.exists(default_ledger_path):
		return default_ledger_path + '/' + name

	# use the actual working dir instead if nothign exists, phew
	else:
		return name



# getting the variables from the settings file - don't change the values here!

aliases = config('aliases')
modify_ledger_file = config('modify_ledger_file')

default_transaction_name = config('default_transaction_name')
default_account_one_name = config('default_account_one_name')
default_receiving_account = config('default_receiving_account')
invoice_transaction_add = config('invoice_transaction_add')
default_commodity = config('default_commodity')
ask_commodity = config('ask_commodity')
ask_account_comment = config('ask_account_comment')
dec_sep = config('dec_sep')
preset_wildcard = config('preset_wildcard')

info_text =  config('info_text')

split_journal_into_years = config('split_journal_into_years')
default_filename = config('default_filename')
default_ledger_path = config('default_ledger_path')
date_format = config('date_format')

afa_accounts = config('afa_accounts')
afa_threshold_amount = config('afa_threshold_amount')
afa_per_day_or_month = config('afa_per_day_or_month')
afa_table = config('afa_table')
afa_def_account = config('afa_def_account')
afanon_def_account = config('afanon_def_account')
afa_append_comment = config('afa_append_comment')

colorize = config('colorize')

CL_TXT = config('CL_TXT')
CL_INF = config('CL_INF')
CL_DEF = config('CL_DEF')
CL_DIM = config('CL_DIM')
CL_ACC = config('CL_ACC')
CL_OUT = config('CL_OUT')
CL_E = config('CL_E')

### ### ###
### ### ### load configurarion file for variables - END
### ### ###



# color info_text
info_text = CL_INF + info_text + CL_E




# check arguments and environment variable 'LEDGER_FILE_PATH' for ledger file
arguments = sys.argv

# no arguments? check environment variable
if len(arguments) < 2:
	ledger_file = journal_file()
	file_automatic = True
else:
	# using the argument as the file
	ledger_file = arguments[1]
	file_automatic = False

# check if it exists and if it's no directory / if it's a real file
if os.path.exists(ledger_file):
	if not os.path.isfile(ledger_file):
		print CL_INF + 'Given \'ledger file\' seems to be a directory.' + CL_E
		exit()
# create new file otherwise
else:
	f = open(ledger_file, 'w')
	f.write('')
	f.close()

# everything is fine, go on!
print CL_TXT + 'Using', ledger_file, 'for computing.' + CL_E



# functions and classes

def get_real_amount_with_percentage(original_amount, percentage, private=False):
	# rounds the last two digits of the real_amount of the Money class
	new = int( original_amount * percentage )
	if int( str(new)[-2:]) >= 50:
		new += 100
	if private:
		return original_amount - int( str(new)[:-2] + '00' )
	else:
		return int( str(new)[:-2] + '00' )

def add_month(dateobj):
	# returns how much months are left, including actual given month
	new_month = dateobj.month + 1
	if new_month > 12:
		new_year = dateobj.year + 1
		new_month = 1
	else:
		new_year = dateobj.year
	return datetime.datetime(new_year,new_month,dateobj.day)

def alias_it(text):
	out = []
	for c, x in enumerate(text.split(':')):
		if x in aliases.keys() and c > 0:
			out.append( aliases[x] )
		else:
			out.append( x )
	return ':'.join(out)

def end(s):
	# exits the programm, if s is a dot - used in the functions of the ledger_class
	if s == '.':
		print
		exit()

def get_date(inp):
	# string into date
	return datetime.datetime.strptime(inp, date_format)

def validate_date(d):
	# simple check, if the string d is a valid date format
	try:
		get_date(d)
		return True
	except ValueError:
		return False


class ledgerer_class(object):
	def __init__(self, the_file):
		if not os.path.isfile(the_file):
			# exits the programm, if the given environment variable or argument is not a file
			print CL_INF + 'Given argument is not a file.' + CL_E
			exit()

		# parse the transactions into self.Journal
		f = open(the_file, 'r')
		the_journal = f.read()
		f.close()
		self.Journal = ledgerparse.string_to_ledger(the_journal)
		# except Exception, e:
		# 	print CL_INF + 'Journal file has a wrong ledger format.' + CL_E
		# 	raise e
		# 	exit()


	def preset_strip_options(self, text):
		# Splits a payee string from preset format into original payee and options

		# get orginal-part
		if text.find('['):
			orig = text[:text.rfind('[')]
		else:
			orig = ''

		# get options-part
		if text.find('['):
			opt = text[text.rfind('[')+1:-1]
		else:
			opt= ''

		return [orig, opt]


	def preset_get_name_and_settings(self, text):
		# Gets the settings from the preset payee, which is on the very end of the payee and inside the []. The format is actually:
		# [NAME: str, KEEP_YEAR: bool, KEEP_MONTH: bool, KEEP_DAY: bool]

		# get name and options from payee text
		text = self.preset_strip_options(text)[1]

		# split variable by ','
		output = []
		for c, x in enumerate(text.split(',')):
			if c == 0:
				output.append(x)
			else:
				try:
					output.append( bool( int(x) ) )
				except Exception:
					output.append( False )

		# give it to me!
		return output


	def save_or_delete_preset(self, delete=''):
		# get the presetlist
		presetlist = self.preset(liste=True)

		# save a preset
		if not delete:
			# get the preset name
			user = raw_input(CL_TXT + 'Preset name [' + CL_DEF + 'preset' + CL_TXT + ']: ' + CL_E)
			if not user:
				new_preset_name = 'preset'
			else:
				new_preset_name = user
			end(user)

			# get options for keeping YEAR, MONTH, DAY
			# year
			user = raw_input(CL_TXT + 'Keep YEAR [' + CL_DEF + 'no' + CL_TXT + ']: ' + CL_E)
			if user == 'yes' or user == 'y':
				keep_year = '1'
			else:
				keep_year = '0'

			# month
			user = raw_input(CL_TXT + 'Keep MONTH [' + CL_DEF + 'no' + CL_TXT + ']: ' + CL_E)
			if user == 'yes' or user == 'y':
				keep_month = '1'
			else:
				keep_month = '0'

			# day
			user = raw_input(CL_TXT + 'Keep DAY [' + CL_DEF + 'no' + CL_TXT + ']: ' + CL_E)
			if user == 'yes' or user == 'y':
				keep_day = '1'
			else:
				keep_day = '0'

			# check if it already exists
			for t in presetlist:

				# it already exists, cancel
				if new_preset_name == t.payee:
					print CL_INF + 'Preset already exists. Delete it first.' + CL_E
					self.date()

			# modify self.final_str to match preset format

			# add options on the end of the first line [NAME,0,0,0] or similar
			tmp_final_str = []
			for numline, line in enumerate(self.final_str.splitlines()):
				if numline == 0:
					tmp_final_str.append( line + '[' + new_preset_name + ',' + keep_year + ',' + keep_month + ',' + keep_day + ']' )
				else:
					tmp_final_str.append( line )
			self.final_str = '\n'.join( tmp_final_str )

			# append it to the file (or create a new file)
			if os.path.isfile(path_to_project + '/ledger-add.presets'):
				print CL_TXT + 'Appending to preset file ...' + CL_E

				# check if file is empty or not
				f = open(path_to_project + '/ledger-add.presets', 'r')
				newlines = '\n\n' if len(f.read()) > 0 else ''
				f.close()

				# write stuff
				f = open(path_to_project + '/ledger-add.presets', 'a')
				f.write(newlines + self.final_str)
				f.close()
				self.date()

			# create a new file
			else:
				print CL_TXT + 'Creating new preset file ...' + CL_E
				f = open(path_to_project + '/ledger-add.presets', 'w')
				f.write(self.final_str)
				f.close()
				self.date()

		# delete a preset
		else:
			new_presets = []
			for t in presetlist:
				# delete it
				options = self.preset_get_name_and_settings(t.payee)
				if delete in options:
					# delete the preset
					cancel = raw_input(CL_INF + 'Really delete the preset [' + CL_DEF + 'no' + CL_INF + ']? ' + CL_E)
					if not cancel or cancel == 'n' or cancel == 'no':
						print CL_TXT + 'Canceling ...' + CL_E
						new_presets.append( t )
				# append the rest
				else:
					new_presets.append( t )

			# save the new file (or the same)
			f = open(path_to_project + '/ledger-add.presets', 'w')
			f.write( '\n\n'.join( [str(x) for x in new_presets] ) )
			f.close()

		# start from beginning
		self.date()


	def preset(self, what='', liste=False):
		# try to load the preset file
		if not os.path.isfile(path_to_project + '/ledger-add.presets'):
			presetjournal = []
		else:
			f = open(path_to_project + '/ledger-add.presets', 'r')
			presetjournal = ledgerparse.string_to_ledger( f.read() )
			f.close()

		# return the list, if liste == True
		if liste == True:
			return presetjournal

		# add the transaction with the presetname to the final_str
		the_sum = 0.0
		for t in presetjournal:

			# use transaction as preset, if name matches - replace stuff as well
			options = self.preset_get_name_and_settings(t.payee)
			if what in options:

				# get options from preset name
				# name
				if len(options) > 0:
					pr_name = options[0]
				else:
					pr_name = ''

				# options
				if len(options) > 3:
					pr_year = options[1]
					pr_month = options[2]
					pr_day = options[3]
				else:
					pr_year = False
					pr_month = False
					pr_day = False

				# get sum and commodity
				for acc in t.accounts:
					try:
						the_sum += float( str(acc.amount).replace(',', '.') )
					except Exception:
						pass
					self.str_commodity = acc.commodity

				# get transaction string without the options
				# and replace date according to options of preset
				tmp_trans = []
				for c, x in enumerate(t.get_original().splitlines()):
					if c == 0:
						tmp_tmp_trans = self.preset_strip_options(x)[0]
						# year
						if not pr_year:
							tmp_tmp_trans = self.str_date[0:4] + tmp_tmp_trans[4:]
						# month
						if not pr_month:
							tmp_tmp_trans = tmp_tmp_trans[0:5] + self.str_date[5:7] + tmp_tmp_trans[7:]
						# day
						if not pr_day:
							tmp_tmp_trans = tmp_tmp_trans[0:8] + self.str_date[8:10] + tmp_tmp_trans[10:]
						tmp_trans.append( tmp_tmp_trans )
					else:
						tmp_trans.append( x )
				self.final_str = '\n'.join(tmp_trans)

				# replace preset_wildcards
				while preset_wildcard in self.final_str:
					print
					print CL_DEF + self.final_str + CL_E
					user = raw_input(CL_TXT + 'Replace first / last ' + CL_DEF + preset_wildcard + CL_TXT + ': ' + CL_E)
					self.final_str = self.final_str.replace(preset_wildcard, user, 1)

		# add the transaction to the journal
		print
		print CL_TXT + '- - - - -' + CL_E
		print CL_OUT + self.final_str + CL_E
		print CL_TXT + '- - - - -' + CL_E
		print CL_DIM + 'Sum of values: ' + str(the_sum).replace('.', ',') + ' ' + self.str_commodity + CL_E
		print

		# ask if output should be appended
		user = raw_input(CL_TXT + 'Add this entry? (yes=appends to file, p=saves as a preset) [' + CL_DEF + 'yes' + CL_TXT + ']: ' + CL_E)
		# go back
		if user == '<':
			self.name()
		if user == 'n' or user == 'no':
			self.date()
		elif user == 'p' or user == 'preset':
			self.save_or_delete_preset()
		else:
			end(user)
			self.append_file()


	def use_code(self, user_code):
		# search this code in the journal
		trans_id = -1
		for i, trans in enumerate(self.Journal):
			if user_code == trans.code:
				trans_id = i

		# if not found, ask for name again
		if trans_id < 0:
			print
			print CL_INF + 'No existing transaction with this code was found. Enter another transaction name, please.' + CL_E
			print
			self.name()

		# found, so assign the needed variables from the found transaction
		else:
			# set up an array for the transaction posts
			self.str_accounts = []
			self.str_accounts_amount = []
			self.str_accounts_comment = []

			# get the transaction name / payee (and state and stuff)
			tmp_code = ' (' + self.Journal[trans_id].code + ') '
			self.str_name = self.Journal[trans_id].state + tmp_code + self.Journal[trans_id].payee + invoice_transaction_add

			# get the transaction comment
			self.str_transaction_comment = '\n ; '.join([c.strip() for c in self.Journal[trans_id].comments])

			# ask which account is the paying account
			for num, acc in enumerate(self.Journal[trans_id].accounts):
				tmp_acc_commodity = ' ' + acc.commodity if acc.commodity else ''
				tmp_acc_amount = ' (' + str(acc.amount).replace('.', dec_sep) + tmp_acc_commodity + ')' if acc.amount != 0 else ''
				print CL_DEF + '(' + str(num+1) + ') ' + acc.name + tmp_acc_amount + CL_E
				# get the commodity as well
				if acc.commodity:
					self.str_commodity = acc.commodity
			# correct commodity, if no commodity was set
			if not self.str_commodity:
				if ask_commodity:
					# change the commodity
					user = raw_input(CL_TXT + 'Commodity [' + CL_DEF + default_commodity + CL_TXT + ']: ' + CL_E)
					# go back
					if user == '<':
						self.name()
					# no input? use default!
					if not user:
						self.str_commodity = default_commodity
					end(user)
				else:
					self.str_commodity = default_commodity
			# go on with the account asking
			print CL_TXT + 'Chose one or more accounts: e.g. "1,2,4"' + CL_E
			user = raw_input(CL_TXT + 'Paying account(s): ' + CL_E )
			# go back
			if user == '<':
				self.name()
			end(user)
			# work with the input, if it's correct
			try:
				for paying_account in [int(splits) for splits in user.split(',')]:
					# get the acconuts name
					self.str_accounts.append( self.Journal[trans_id].accounts[int(paying_account)-1].name )
					# get the accounts amount
					self.str_accounts_amount.append( self.Journal[trans_id].balance_account(int(paying_account)-1, True) )
					# get the accounts comments
					self.str_accounts_comment.append( '\n ; '.join([c.strip() for c in self.Journal[trans_id].accounts[int(paying_account)-1].comments]) )
			except Exception:
				print CL_INF + 'Wrong input, try again.' + CL_E
				self.use_code(user_code)

			# ask which account is the receiving account
			user = raw_input(CL_TXT + 'Receiving account [' + CL_DEF + default_receiving_account + CL_TXT + ']: ' + CL_E )
			# go back
			if user == '<':
				self.name()
			end(user)
			# use default, if no input
			if not user:
				user = default_receiving_account
			# set the acconuts name
			self.str_accounts.append( alias_it(user) )
			# set the accounts amount
			self.str_accounts_amount.append( 0.0 )
			# add blank comment to this
			self.str_accounts_comment.append('')

			# finally make the output
			self.final_add()


	def date(self):
		print

		# print info_text
		print info_text

		# the actual date, used as a default template
		self.today = datetime.datetime.now().strftime(date_format)

		user = ''
		# repeat while the input is not a valid date (so it goes on, if the user inputs a correct date)
		input_correct = False
		while not input_correct:
			user = raw_input(CL_TXT + 'Date [' + CL_DEF + self.today + CL_TXT + ']: ' + CL_E)
			# if user inputs nothing, use the default (today)
			if not user:
				user = self.today
				input_correct = validate_date(user)
			else:
				# check if it a day difference or a valid date
				try:
					# it is a day difference
					difference = int(user)
					new_date = datetime.datetime.now() + datetime.timedelta(days=difference)
					user = new_date.strftime(date_format)
					input_correct = validate_date(user)
				except Exception, e:
					# it's a valid date ... or not
					input_correct = validate_date(user)
			# or tell the user that it is wrong ... or end the programm if it's a '.'
			if not input_correct:
				end(user)
				print CL_INF + 'Wrong input.' + CL_E
		self.str_date = get_date(user).strftime(date_format)
		self.name()


	def name(self):
		# gets the name of the transcation. this is a string, no big checks are needed e.g. regarding the format.

		# get and print the presets
		presets = self.preset(liste=True)
		preset = False
		preset_names = []
		for t in presets:
			preset_names.append( self.preset_get_name_and_settings(t.payee)[0] )
		print CL_DIM + 'Available presets: ' + CL_DEF + ', '.join(preset_names) + CL_E
		print CL_DIM + '"p PRESETNAME" = chose preset. "d PRESETNAME" = delete preset.' + CL_E
		user = raw_input(CL_TXT + 'Name or preset [' + CL_DEF + default_transaction_name + CL_TXT + ']: ' + CL_E)
		end(user)
		# go back
		if user == '<':
			self.date()
		# check for preset command
		if len(user) > 2:
			if user[0:2] == 'p ':
				# input correct?
				preset = self.preset(user[2:])
			elif user[0:2] == 'd ':
				# delete a preset
				self.save_or_delete_preset(delete=user[2:])
		# check for afa command (to add afa transactions, while original already exists)
		if len(user) > 3:
			if user[0:3] == 'afa':
				self.post_afa(user[3:])
		# fill user with default, if nothing was input
		if not user:
			user = default_transaction_name


		# cleared / pending feature ... only if enabled in configuration file (modify_ledger_file) ... it will find and clear the trans.
		if user[0:2] == '* ' and modify_ledger_file:
			# getting the original data
			f = open(ledger_file, 'r')
			original_raw = f.read()
			original = original_raw.splitlines()
			f.close()

			# search line in which the to-be-cleared transaction is in (it has to have a '!' as well)
			# and search endline, used in output-showing
			line = -1
			for y, x in enumerate(original):
				if user[2:] in x and '!' in x:
					line = y
			endline = -1
			for x in xrange(line, len(original)):
				if original[x] == '' or x == len(original)-1:
					endline = x
					break

			# modify this specific line
			if line > -1:
				old_startdate = original[line][0: original[line].find(' ') ]
				old_transaction = original[line][ original[line].find('!')+2: ]
				original[line] = old_startdate + '=' + self.str_date + ' * ' + old_transaction

				# show and ask for modification
				print
				print CL_TXT + '- - - - -' + CL_E

				for x in xrange(line,endline):
					print original[x]

				print CL_TXT + '- - - - -' + CL_E
				print

				# ask if output should be appended
				user = raw_input(CL_TXT + 'Modify this entry this way? [' + CL_DEF + 'yes' + CL_TXT + ']: ' + CL_E)
				# go back
				if user == 'n' or user == 'no':
					self.date()
				else:
					end(user)

					output = '\n'.join(original)
					f = open(ledger_file, 'w')
					f.write( output )
					f.close()
					self.sort_journal(ledger_file)
					self.date()

		# a simple code was input "(200)" so use this transactions values form an existing one
		if user[0:1] == '(' and user[-1:] == ')':
			self.use_code(user[1:-1])

		# add cleared if not pending state was set
		if not user[0:2] == '! ':
			user = '* ' + user
		end(user)

		# preset or manual input?
		if preset:
			self.final_add()
		else:
			self.str_name = user
			self.transaction_comment()


	def transaction_comment(self):
		# gets the comment for the transaction. again: no big checkings are needed, string only
		user = raw_input(CL_TXT + 'Transaction comment: ' + CL_E)
		# go back
		if user == '<':
			self.name()
		end(user)
		if user:
			user2 = raw_input(CL_TXT + 'Transaction comment 2: ' + CL_E)
			end(user2)
			if user2:
				user += '\n ; ' + user2
		self.str_transaction_comment = user
		if ask_commodity:
			self.commodity()
		else:
			self.str_commodity = default_commodity
			self.accounts()


	def commodity(self):
		# change the commodity
		user = raw_input(CL_TXT + 'Commodity [' + CL_DEF + default_commodity + CL_TXT + ']: ' + CL_E)
		# go back
		if user == '<':
			self.transaction_comment()
		# no input? use default!
		if not user:
			user = default_commodity
		end(user)
		self.str_commodity = user
		self.accounts()


	def accounts(self):
		global default_account_one_name

		# set up an array for the transaction posts
		self.str_accounts = []
		self.str_accounts_amount = []
		self.str_accounts_comment = []

		# generate correct default account name
		if '{name}' in default_account_one_name:
			default_account_one_name_str = default_account_one_name.replace('{name}', self.str_name.replace('* ', '').replace('! ',''))
		else:
			default_account_one_name_str = default_account_one_name

		# get the first transaction post
		user = raw_input(CL_TXT + 'Account 1 name [' + CL_DEF + default_account_one_name_str + CL_TXT + ']: ' + CL_E)
		# go back
		if user == '<':
			if ask_commodity:
				self.commodity()
			else:
				self.transaction_comment()
		# no input? use default!
		if not user:
			user = default_account_one_name_str
		end(user)
		self.str_accounts.append( alias_it(user) )

		# gets the amount for the transaction. first transaction post needs an amount
		account_one_amount = False
		while not account_one_amount:
			user = raw_input(CL_TXT + 'Account 1 amount: ' + CL_E)
			# go back
			if user == '<':
				if ask_commodity:
					self.commodity()
				else:
					self.transaction_comment()
			if not user:
				print CL_INF + 'First account needs an amount.' + CL_E
			else:
				account_one_amount = True
		end(user)
		self.str_accounts_amount.append(user)

		# get the comment for the first account
		if ask_account_comment:
			user = raw_input(CL_TXT + 'Account 1 comment: ' + CL_E)
			if user == '<':
				if ask_commodity:
					self.commodity()
				else:
					self.transaction_comment()
			end(user)
			self.str_accounts_comment.append(user)
		else:
			self.str_accounts_comment.append('')

		# at least one more post is needed for transaction. repeat 'while' until a correct input is done
		account_next = True
		account_next_atleast_one_amount = False
		account_next_number = len(self.str_accounts)+1
		while account_next:
			# since it can be more than 2 posts, repeat until the account / post name is blank ...
			user = raw_input(CL_TXT + 'Account ' + str(account_next_number) + ': ' + CL_E)
			# go back
			if user == '<':
				self.commodity()
			if not user:
				# ... but repeat if there are not at least 2 posts at all
				if len(self.str_accounts) < 2:
					print CL_INF + 'Need at least 2 accounts.' + CL_E
				else:
					account_next = False
			else:
				end(user)
				self.str_accounts.append( alias_it(user) )

				# also check for the specific amount
				account_next_amount = True
				while account_next_amount:
					user = raw_input(CL_TXT + 'Account ' + str(account_next_number) + ' amount: ' + CL_E)
					# go back
					if user == '<':
						self.commodity()
					# one post may have a blank amount (ledger auto calculate) the others must have an amount
					if not user and account_next_atleast_one_amount:
						print CL_INF + 'Only one account may not have an amount.' + CL_E
					elif not user and not account_next_atleast_one_amount:
						account_next_atleast_one_amount = True
						account_next_amount = False
						end(user)
						self.str_accounts_amount.append(user)
					else:
						account_next_amount = False
						end(user)
						self.str_accounts_amount.append(user)

				# and get the comment for the specific account as well
				if ask_account_comment:
					user = raw_input(CL_TXT + 'Account ' + str(account_next_number) + ' comment: ' + CL_E)
					if user == '<':
						if ask_commodity:
							self.commodity()
						else:
							self.transaction_comment()
					end(user)
					self.str_accounts_comment.append(user)
				else:
					self.str_accounts_comment.append('')

				account_next_number += 1

		self.final_add()


	def final_add(self):
		print
		print CL_TXT + '- - - - -' + CL_E

		# combine the variables to a single string
		# first the date and name of the transaction
		self.final_str = self.str_date + ' ' + self.str_name + '\n'
		# add the comment, but only if there is a comment set
		if not self.str_transaction_comment == '':
			self.final_str += ' ; ' + self.str_transaction_comment + '\n'
		# add all the transactin posts, which are there
		for x in xrange(0, len(self.str_accounts) ):
			self.final_str += ' ' + self.str_accounts[x]
			# also add its amount, if there is one given
			if self.str_accounts_amount[x]:
				self.final_str += '  ' + self.str_commodity + ' ' + self.str_accounts_amount[x]
			# add the comment, if there is one
			if self.str_accounts_comment[x]:
				self.final_str += '\n ; ' + self.str_accounts_comment[x]
			# add a line, if it's not the last entry
			if not x == len(self.str_accounts)-1:
				self.final_str += '\n'
		# sum all amounts for informational output
		the_sum = 0.0
		for x in self.str_accounts_amount:
			try:
				the_sum += float( x.replace(',', '.') )
			except Exception:
				pass
		print CL_OUT + self.final_str + CL_E
		print CL_TXT + '- - - - -' + CL_E
		print CL_DIM + 'Sum of values: ' + str(the_sum).replace('.', ',') + ' ' + self.str_commodity + CL_E
		print

		# ask if output should be appended
		user = raw_input(CL_TXT + 'Add this entry? (yes=appends to file, p=saves as a preset) [' + CL_DEF + 'yes' + CL_TXT + ']: ' + CL_E)
		# go back
		if user == '<':
			self.accounts()
		if user == 'n' or user == 'no':
			self.date()
		elif user == 'p' or user == 'preset':
			self.save_or_delete_preset()
		else:
			end(user)
			self.append_file()


	def sort_journal(self, file):
		# sort the given ledger journal file
		# !!! !!! !!!
		# ATTENTION: if I made a mistake, this could destroy the whole journal !!!
		# !!! !!! !!!

		# check if file exists
		if os.path.isfile(file):
			f = open(file, 'r')
			the_journal = f.read()
			f.close()
		else:
			print 'Argument is not an existing file!'
			return

		# get everything besides the transactions
		the_journal_other = ledgerparse.string_to_non_transactions(the_journal)
		if the_journal_other:
			the_journal_other += '\n\n'

		# sort it
		the_journal_sorted = '\n\n'.join([str(x.get_original()) for x in sorted(ledgerparse.string_to_ledger(the_journal), key=lambda y: y.date)])

		# save it to the SAME file !!!!!!
		f = open(file, 'w')
		f.write(the_journal_other + the_journal_sorted)
		f.close()


	def append_file(self):
		print CL_TXT + 'Adding entry ...' + CL_E

		# getting the original data
		f = open(ledger_file, 'r')
		original_raw = f.read()
		original = original_raw.splitlines()
		f.close()


		# first check, if the file is empty: then just append / write new
		if len(original) < 1:
			f = open(ledger_file, 'w')
			f.write(self.final_str)
			f.close()

		# simple append to the given file
		elif len(original) > 1:

			f = open(ledger_file, 'a')
			f.write('\n\n' + self.final_str)
			f.close()

		# sort the file, if modify_ledger_file is True
		if modify_ledger_file:
			self.sort_journal(ledger_file)

		# check for afa feature
		# if it is not disabled ...
		if not 'disabled' in afa_accounts:
			# ... check for afa_accounts
			if len(afa_accounts) > 0:
				# ... check if one entered account is in the afa_accounts
				for afa_check in afa_accounts:
					for str_accs in self.str_accounts:
						if afa_check.lower() in str_accs.lower():
							self.afa_feature()
			# ... or ask for input
			else:
				print
				user = raw_input(CL_TXT + 'Use AfA feature [' + CL_DEF + 'no' + CL_TXT + '] ? ' + CL_E)
				end(user)
				# no or nothing? beginn from the very beginning
				if user == 'n' or user == 'no' or not user:
					print
					self.date()
				else:
					self.afa_feature()

		# start from the beginning
		print
		self.date()


	def post_afa(self, code):
		code = code.strip()
		# get rid of possible braces
		if '(' in code and ')' in code:
			code = code[1:-1]

		# search this code in the journal
		trans_id = -1
		for i, trans in enumerate(self.Journal):
			if code == trans.code:
				trans_id = i
				break
		if trans_id < 0:
			print
			print CL_INF + 'No existing transaction with this code was found. Enter another transaction name, please.' + CL_E
			print
			self.name()
		original_trans = self.Journal[trans_id]

		# use this transaction?
		print
		print CL_TXT + '- - - - -' + CL_E
		print original_trans
		print CL_TXT + '- - - - -' + CL_E
		user = raw_input(CL_TXT + 'Use this transaction [' + CL_DEF + 'yes' + CL_TXT + '] ? ' + CL_E)
		if not user or user == 'y' or user == 'yes':
			self.afa_feature(original_trans)
		else:
			self.name()


	def afa_feature(self, trans=None):
		# convert transaction to ledger_transaction or take from argument
		if not trans:
			trans = ledgerparse.string_to_ledger(self.final_str)[0]

		# make one afa reduction for every posted account with amount > 0
		all_afas = []
		for acc in trans.accounts:
			if acc.amount.amount > 0:
				# get its comment for output
				tmp_acc_com = ' (' + ', '.join([x.strip() for x in acc.comments]) + ')' if len(acc.comments) > 0 else ''
				print
				print CL_TXT + 'Transaction: (' + CL_DEF + trans.code + CL_TXT + ') ' + CL_ACC + trans.payee + CL_E
				print CL_TXT + 'Account: ' + CL_ACC + acc.name + CL_DIM + tmp_acc_com + ' ' + str(acc.amount) + ' ' + acc.commodity + CL_E
				# ask percentage of usage
				user = raw_input(CL_TXT + 'Usage for the job [' + CL_DEF + '100' + CL_TXT + ']% ? ' + CL_E)
				if not user:
					user = '100'
				try:
					percentage = float(user) / 100
				except Exception:
					percentage = 1.0
				# choose type of afa stuff
				print CL_TXT + 'What is it? (Enter number or string for manual input.)' + CL_E
				for num, item in enumerate(afa_table):
					print CL_TXT + '(' + CL_DEF + str(num+1) + CL_TXT + ') ' + item + CL_DIM + ' (' + str(afa_table[item][0]) + ')' + CL_E

				# let the user chose the afa item
				correct = False
				while not correct:
					user = raw_input(CL_TXT + afa_def_account + ':' + CL_E)
					end(user)
					if user:
						try:
							# user enters number
							if afa_table.keys()[int(user)-1] in afa_table:
								afa_item = afa_table.keys()[int(user)-1]
								afa_item_years = afa_table[afa_item][0]
								afa_item_name = afa_table[afa_item][1]
								correct = True
						except Exception:
							try:
								# user enters string
								afa_item_name = alias_it( afa_def_account + ':' + user )
								afa_item_years = raw_input(CL_TXT + 'Years: ' + CL_E)
								end(user)
								if not afa_item_years:
									afa_item_years = 1
								else:
									afa_item_years = int(afa_item_years)
								correct = True
							except Exception:
								print CL_INF + 'Chose correct entry or enter string.' + CL_E


				# NONAFA here !!
				# generate the nonafa transaction, if percentage is < 1.0
				# NONAFA here !!

				if percentage < 1.0:
					# get code
					tmp_nonafa_code = '(' + trans.code + ') ' if trans.code else ''

					# get comment
					tmp_nonafa_comment = '\n ;' + '\n ;'.join(trans.comments) if len(trans.comments) > 0 else ''
					tmp_nonafa_acc_comment = '\n ;' + '\n ;'.join(acc.comments) if len(acc.comments) > 0 else ''
					if afa_append_comment:
						tmp_nonafa_comment += tmp_nonafa_acc_comment
						tmp_nonafa_acc_comment = ''

					# make account
					tmp_nonafa_account = afa_item_name.replace('[ACCOUNT]', afanon_def_account)

					# get amount
					tmp_real_amount = get_real_amount_with_percentage(acc.amount.amount, percentage, True)

					# generate nonafa transaction (on the same day)
					tmp_nonafa = trans.date.strftime(date_format) + ' * ' + tmp_nonafa_code + trans.payee + tmp_nonafa_comment + '\n ' + tmp_nonafa_account + '  ' + default_commodity + ' ' + str(ledgerparse.Money(real_amount=tmp_real_amount, dec_sep=dec_sep)) + '\n ' + acc.name + tmp_nonafa_acc_comment

					# append it
					all_afas.append( (trans.date.year, tmp_nonafa) )

				# generate a single afa transaction, while it's bellow the afa_threshold
				if acc.amount.amount < afa_threshold_amount * 10000:
					all_afas.extend( self.afa_generate_trans(trans, acc, afa_item_name.replace('[ACCOUNT]', afa_def_account), percentage=percentage) )
				# generate transactions over X year, where X = afa_item_years
				else:
					if afa_per_day_or_month == 'day':
						per_amount = ledgerparse.Money( real_amount=int( str( get_real_amount_with_percentage(acc.amount.amount, percentage) / (365 * afa_item_years) ).replace('.', dec_sep)[:-2] + '00' ), dec_sep=dec_sep )
					else:
						per_amount = ledgerparse.Money( real_amount=int( str( get_real_amount_with_percentage(acc.amount.amount, percentage) / (12 * afa_item_years) ).replace('.', dec_sep)[:-2] + '00' ), dec_sep=dec_sep )
					all_afas.extend( self.afa_generate_trans(trans, acc, afa_item_name.replace('[ACCOUNT]', afa_def_account), per_amount, percentage) )

		# append the transactions to the journal(s)

		# only append to a single journal when split_journal_into_years == False
		if not split_journal_into_years or not file_automatic:
			# generate append string
			appender = '\n\n' + '\n\n'.join([x[1] for x in all_afas])

			# append to the file
			f = open(ledger_file, 'a')
			f.write( appender )
			f.close()

			# sort the file, if modify_ledger_file is True
			if modify_ledger_file:
				self.sort_journal(ledger_file)

		# cycle through the years and append to the journals (or create a new journal for this year)
		else:
			for years in all_afas:
				# generate filename
				tmp_file = journal_file(year=years[0])

				# check if file exists
				if os.path.isfile(tmp_file):

					# get file contents length and let append be either \n\n on file or direct the first entry in this file
					f = open(tmp_file, 'r')
					appender_pre = '\n\n' if len(f.read()) > 0 else ''
					f.close()

					# append to file
					f = open(tmp_file, 'a')
					f.write( appender_pre + years[1] )
					f.close()

					# sort the file, if modify_ledger_file is True
					if modify_ledger_file:
						self.sort_journal(ledger_file)

				# file does not exist so create totally new
				else:
					f = open(tmp_file, 'w')
					f.write( years[1] )
					f.close()

					# sort the file, if modify_ledger_file is True
					if modify_ledger_file:
						self.sort_journal(ledger_file)

		print
		self.date()

	def afa_generate_trans(self, trans, account_expense, account_afa, per_amount=None, percentage=1.0):
		# outputs an array with tuple like this:
		# [ (YEAR: integer, TRANSACTION: string), ... ]

		# get basic general values
		tmp_code = '(' + trans.code + ') ' if trans.code else ''


		# append comment of expense account to afa account as well, if enabled
		# (by ONLY append it to the transaction)
		tmp_comment = '\n ;' + '\n ;'.join(trans.comments) if len(trans.comments) > 0 else ''
		tmp_acc_comment = '\n ;' + '\n ;'.join(account_expense.comments) if len(account_expense.comments) > 0 else ''
		if afa_append_comment:
			tmp_comment += tmp_acc_comment
			tmp_acc_comment = ''

		# get amount
		tmp_real_amount = get_real_amount_with_percentage(account_expense.amount.amount, percentage)

		# starting year (an expense can only be used the next day it was bought)
		starting_date = (trans.date + datetime.timedelta(days=1))

		# make a single transaction
		if type(per_amount).__name__ != 'Money':
			return [ (starting_date.year, datetime.datetime(starting_date.year, 12, 31).strftime(date_format) + ' * ' + tmp_code + trans.payee + tmp_comment + '\n ' + account_afa + '  ' + default_commodity + ' ' + str(ledgerparse.Money(real_amount=tmp_real_amount, dec_sep=dec_sep)) + '\n ' + account_expense.name + tmp_acc_comment) ]
		# make one transactions per year, till the acc.amount is <= 0 - subtracted by per_amount per day
		else:
			output = []
			starting_amount = ledgerparse.Money(real_amount=tmp_real_amount, dec_sep=dec_sep)
			actual = starting_date

			# subtract from starting_amount till it's 0
			while starting_amount.amount > 0:

				# add substraction amount for actual year
				working = actual
				amount = ledgerparse.Money(dec_sep=dec_sep)
				while working.year == actual.year:
					# per_amount is lower than the remaining starting_amount
					if starting_amount.amount > per_amount.amount:
						amount += per_amount
						starting_amount -= per_amount
						if afa_per_day_or_month == 'day':
							working = working + datetime.timedelta(days=1)
						else:
							working = add_month(working)
					# the remaining starting_amount is below per_amount ... it has to be the last year so add the last cent to the amount
					elif starting_amount.amount <= per_amount.amount:
						amount += starting_amount
						starting_amount.amount = 0
					if starting_amount.amount <= 0:
						working = working + datetime.timedelta(days=365)


				# generate transaction for this year
				output.append( (actual.year, datetime.datetime(actual.year, 12, 31).strftime(date_format) + ' * ' + tmp_code + trans.payee + tmp_comment + '\n ' + account_afa + '  ' + default_commodity + ' ' + str(amount) + '\n ' + account_expense.name + tmp_acc_comment) )

				# go to next year
				actual = datetime.datetime(working.year,1,1)

			# return output for multiple years
			return output




# starting program

ledgerer = ledgerer_class(ledger_file)

ledgerer.date()