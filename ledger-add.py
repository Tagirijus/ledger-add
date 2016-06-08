# coding=utf-8

#
# Programm for adding simple ledger transactions.
# There's a preset system: Press 'p' to chose a preset and save one in the final prompt.
#

import os, sys, datetime, imp


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
		print 'Please update your personal settings file.'
		return getattr(configuration_def, att)



# getting the variables from the settings file - don't change the values here!

modify_ledger_file = config('modify_ledger_file')

default_transaction_name = config('default_transaction_name')
default_account_one_name = config('default_account_one_name')
default_commodity = config('default_commodity')
ask_commodity = config('ask_commodity')

info_text	 =  config('info_text')

colorize = config('colorize')

CL_TXT = config('CL_TXT')
CL_INF = config('CL_INF')
CL_DEF = config('CL_DEF')
CL_DIM = config('CL_DIM')
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
	try:
		ledger_file = os.environ['LEDGER_FILE_PATH'] + '/ledger_' + datetime.datetime.now().strftime('%Y') + '.journal'
	except Exception:
		# nothing set, quit programm
		print CL_INF + 'No arguments given and environment variable LEDGER_FILE_PATH is not set.' + CL_E
		exit()
else:
	# using the argument as the file
	ledger_file = arguments[1]

# check if it exists and if it's a real file
if os.path.exists(ledger_file):
	if not os.path.isfile(ledger_file):
		print CL_INF + 'Given \'ledger file\' is not a file.' + CL_E
		exit()
# create new file otherwise
else:
	f = open(ledger_file, 'w')
	f.write('')
	f.close()

# everything is fine, go on!
print CL_TXT + 'Using', ledger_file, 'for computing.' + CL_E



# functions and classes

def end(s):
	# exits the programm, if s is a dot - used in the functions of the ledger_class
	if s == '.':
		print
		exit()

def get_date(inp):
	# string into date
	return datetime.datetime.strptime(inp, '%Y/%m/%d')

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


	def preset(self, what):
		# load preset file, if possible, create empty array otherwise
		if os.path.isfile(path_to_project + '/ledger-add.presets'):
			# load file into variable
			preset_file = open(path_to_project + '/ledger-add.presets', 'r')
			self.preset_file_raw = preset_file.readlines()
			self.preset_content = []
			for x in self.preset_file_raw:
				self.preset_content.append(x.rstrip().split('´'))
			preset_file.close()
		else:
			preset_file = open(path_to_project + '/ledger-add.presets', 'w')
			preset_file.write('')
			preset_file.close()
			self.preset_content = []

		# check if its preset chosing
		if what[0:2] == 'p ':

			# get preset name
			preset_name = what[2:]

			# chose preset, or return not-found message + False
			which = -1
			for y, x in enumerate(self.preset_content):
				if x[0] == preset_name:
					which = y
			if which < 0:
				print CL_INF + 'Preset not found.' + CL_E
				return False

			# get its values from found preset
			# get name, comment and commodity
			self.str_name = self.preset_content[which][1]
			self.str_transaction_comment = self.preset_content[which][2]
			self.str_commodity = self.preset_content[which][3]

			# get accounts and accounts_amonut array
			self.str_accounts = []
			self.str_accounts_amount = []
			c = 1
			for x in xrange(4, len(self.preset_content[which]) ):
				if c == 1:
					self.str_accounts.append(self.preset_content[which][x])
					c += 1
				elif c == 2:
					self.str_accounts_amount.append(self.preset_content[which][x])
					c -= 1
			return True

		# or list / print out the presets
		elif what == 'list':
			print CL_TXT + 'Presets: ' + CL_DEF + ', '.join(str(x[0]) for x in self.preset_content) + CL_E
			return False

		# otherwise return False
		return False


	def date(self):
		print

		# print info_text
		print info_text

		# the actual date, used as a default template
		self.today = datetime.datetime.now().strftime('%Y/%m/%d')

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
					user = new_date.strftime('%Y/%m/%d')
					input_correct = validate_date(user)
				except Exception, e:
					# it's a valid date ... or not
					input_correct = validate_date(user)
			# or tell the user that it is wrong ... or end the programm if it's a '.'
			if not input_correct:
				end(user)
				print CL_INF + 'Wrong input.' + CL_E
		self.str_date = get_date(user).strftime('%Y/%m/%d')
		self.name()


	def name(self):
		# gets the name of the transcation. this is a string, no big checks are needed e.g. regarding the format.
		preset = self.preset('list')
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
				preset = self.preset(user)
			elif user[0:2] == 'd ':
				# delete a preset
				self.save_preset(delete=user[2:])
		if not user:
			user = default_transaction_name

		# cleared / pending feature ... only if enabled in configuration file ... it will find and clear the trans.
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
					self.date()

		# add clared if not pending state was set
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
			end(user)
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
		self.str_accounts.append(user)

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
				self.str_accounts.append(user)

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
						account_next_number += 1
						end(user)
						self.str_accounts_amount.append(user)
					else:
						account_next_amount = False
						account_next_number += 1
						end(user)
						self.str_accounts_amount.append(user)

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
			if not x == len(self.str_accounts)-1:
				self.final_str += '\n'
		print CL_OUT + self.final_str + CL_E
		print CL_TXT + '- - - - -' + CL_E
		print

		# ask if output should be appended
		user = raw_input(CL_TXT + 'Add this entry? (yes=appends to file, p=saves as a preset) [' + CL_DEF + 'yes' + CL_TXT + ']: ' + CL_E)
		# go back
		if user == '<':
			self.accounts()
		if user == 'n' or user == 'no':
			self.date()
		elif user == 'p' or user == 'preset':
			self.save_preset()
		else:
			end(user)
			self.append_file()


	def save_preset(self, delete=''):
		if not delete:
			# get the preset name
			user = raw_input(CL_TXT + 'Preset name [' + CL_DEF + 'preset' + CL_TXT + ']: ' + CL_E)
			if not user:
				new_preset_name = 'preset'
			else:
				new_preset_name = user
			end(user)
		else:
			# get the preset name to delete
			new_preset_name = delete

		# get the lines of the file
		self.preset('')

		# check if the new preset name is already in the file
		which = -1
		for y, x in enumerate(self.preset_content):
			if x[0] == new_preset_name:
				which = y

		# override existing preset or cancel
		if not which < 0 and not delete:
			cancel = raw_input(CL_TXT + 'Override existing preset [' + CL_DEF + 'no' + CL_TXT + ']? ' + CL_E)
			if not cancel:
				print CL_TXT + 'Canceling ...' + CL_E
				self.date()

			# no cancelling, override data for chosen preset
			self.preset_file_raw[which] = new_preset_name
			self.preset_file_raw[which] += '´' + self.str_name
			self.preset_file_raw[which] += '´' + self.str_transaction_comment
			self.preset_file_raw[which] += '´' + self.str_commodity
			for x in xrange( 0, len(self.str_accounts) ):
				self.preset_file_raw[which] += '´' + self.str_accounts[x]
				self.preset_file_raw[which] += '´' + self.str_accounts_amount[x]

		elif delete and which > -1:
			# delete the preset
			cancel = raw_input(CL_TXT + 'Really delete the preset [' + CL_DEF + 'no' + CL_TXT + ']? ' + CL_E)
			if not cancel:
				print CL_TXT + 'Canceling ...' + CL_E
				self.date()

			# no cancelling, delete the preset
			self.preset_file_raw.pop(which)

		elif delete and which < 0:
			# delete preset not founCL_TXT + d + CL_E
			print CL_INF + 'Preset not found.' + CL_E
			self.date()

		elif not delete:
			# generate new data for new preset
			tmp = new_preset_name
			tmp += '´' + self.str_name
			tmp += '´' + self.str_transaction_comment
			tmp += '´' + self.str_commodity
			for x in xrange( 0, len(self.str_accounts) ):
				tmp += '´' + self.str_accounts[x]
				tmp += '´' + self.str_accounts_amount[x]
			self.preset_file_raw.append(tmp)

		# generate final output string
		final_output = ''
		for x in self.preset_file_raw:
			final_output += x.rstrip() + '\n'

		# override file
		preset_file = open(path_to_project + '/ledger-add.presets', 'w')
		preset_file.write(final_output)
		preset_file.close()
		print CL_TXT + 'Saved to preset file.' + CL_E

		# start from beginning
		self.date()


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

		# add new entry on correct position, if configuration for this feature is enabled
		elif len(original) > 1 and modify_ledger_file:

			# some markers to find the index for the date before new entrys date and the one after it
			before_new 		= -1
			before_new_end 	= -1
			after_new 		= -1
			# and get the date as da dateimte object from the entry
			new_entry_date = get_date( self.str_date )

			# check if there is a date after the new entrys date and get its position
			for x in xrange(0, len(original)):
				# check if the actual line contains a date (the first 10 characters)
				if validate_date( original[x][0:10] ):
					# check if the found lines date is above new entrys date
					if new_entry_date < get_date( original[x][0:10] ):
						after_new = x
						break

			# there is a date after, search for date before new entrys date
			if after_new > -1:
				for x in xrange(after_new, -1, -1):
					# check if the actual line contains a date (the first 10 characters)
					if validate_date( original[x][0:10] ):
						# check if the found lines date is under new entrys date
						if new_entry_date > get_date( original[x][0:10] ):
							before_new = x
							# search end of before-entry
							for y in xrange(x, after_new):
								if original[y] == '':
									before_new_end = y
									break
							break

				# prepare output string
				output_content = ''

				# there is a date before, add antry in between
				added = False
				if before_new > -1:
					for x in xrange(0, len(original)):
						# just add a line into the ouput string
						if x < before_new_end or added:
							output_content += original[x]
						# or add the new entry
						else:
							output_content += '\n' + self.final_str + '\n'
							added = True

						# add line break if it is not the last line
						if x < len(original)-1:
							output_content += '\n'

				# there is no date before, add it as first entry
				else:
					output_content += self.final_str + '\n\n' + original_raw


				# write ouput string
				f = open(ledger_file, 'w')
				f.write(output_content)
				f.close()

			# there is no date after new entrys date - it has to be the newest - so just append
			else:
				f = open(ledger_file, 'a')
				f.write('\n\n' + self.final_str)
				f.close()

		# simple append to the given file
		elif len(original) > 1 and not modify_ledger_file:

			f = open(ledger_file, 'a')
			f.write('\n\n' + self.final_str)
			f.close()

		# start from the beginning
		print
		self.date()





# starting program

ledgerer = ledgerer_class(ledger_file)

ledgerer.date()