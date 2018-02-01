# gist: https://gist.github.com/4397792
# Usage:
# session = cgd.CgdSession(uid, password)
# session.login()
# session.load_latest_transactions(account_key)

# 'session.known_accounts' is now populated with the initial accounts taken from the login response, 
# and the data for the 'account_key' account.

# session.load_latest_transactions(account_key) loads the latest transactions and balances for a given account.

# The CGD API is very "screen-driven" for their app, so this ends up being a rather convoluted way to get data.
# But it works for me, so it might work for someone else.

import requests
from functools import wraps
from pprint import pformat
from decimal import Decimal
from datetime import datetime, timedelta
from os import path
import itertools
import json

def with_base(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        return "https://m.caixadirecta.cgd.pt"+f(*args, **kwds)
    return wrapper

class Urls:
  @staticmethod
	@with_base
	def authentication(user_id):
		return "/apps/r/co/li?u="+user_id

	@staticmethod
	@with_base
	def account_balance(account_key):
		return "/apps/r/cnt/sm/"+account_key

	@staticmethod
	@with_base
	def account_details(account_key):
		return "/apps/r/cnt/dc/"+account_key

	@staticmethod
	@with_base
	def account_more_details():
		return "/apps/r/cnt/dc/m"

class CgdException(RuntimeError):
	pass

class CgdCommunicationException(CgdException):
	"""There was an error communicating with the CGD API"""

class InternalCgdException(CgdException):
	"""Something went wrong inside this library"""



def populate_object_from_mapping_and_conversions(obj, json, mapping, conversions = {}):
	errors = []
	for k,v in mapping.items():
		if not json.has_key(k):
			errors.append("missing key '%s' corresponding to property '%s'" % (k,v))
			continue
		value = json[k]
		if conversions.has_key(k):
			value = conversions[k](value)
		setattr(obj, v, value)

	if any(errors):
		message = """
Errors while parsing from 
%s
Errors:
\t%s""" % (pformat(json), "\n\t".join(errors))
		raise CgdCommunicationException(message)
	return obj


def serialize_date(date):
	return date.strftime("%Y-%m-%dT%H:%M:%S%z")

def deserialize_date(date_string):
	return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

def deserialize_money(money_int):
	return money_int/Decimal(100)

def deserialize_transaction_type(type_string):
	l = type_string.lower()
	if l == 'c':
		return 'credit'
	if l == 'd':
		return 'debit'
	return 'unknown transaction type '+type_string



def create_requests_session():
	requests.defaults.defaults['base_headers'].clear()
	proxies = {
		#"https": "127.0.0.1:8888",
	}
	headers = {
		"X-CGD-APP-Device":"w8",
		"X-CGD-APP-Version":"2.1",
	}
	return requests.session(headers = headers, proxies = proxies)

class Transaction:
	@classmethod
	def from_account_details_transactions(cls, transaction_json):
		mapping = {
			'des':'description',
			'dt':'date',
			'dtv':'transaction_date',
			'moeo': 'original_currency',
			'mon': 'amount',
			'ndc': 'document_number',
			'nmv': 'movement_number',
			'saps': 'balance_after',
			'sdaps': 'available_balance_after',
			'tpm': 'transaction_type',
		}
		conversions = {
			'dt':deserialize_date,
			'dtv':deserialize_date,
			'mon':deserialize_money,
			'saps':deserialize_money,
			'sdaps':deserialize_money,
			'tpm': deserialize_transaction_type
		}
		return populate_object_from_mapping_and_conversions(Transaction(), transaction_json, mapping, conversions)

class Balance:
	@classmethod
	def from_balance_movements(cls, balance_movements_slds):
		mapping = {
			'moe': 'currency',
			'ldd': 'available_overdraft',
			'ldde': 'available_overdraft_euros',
			'scne': 'balance_euros',
			'scnt': 'balance_currency',
			'sdse': 'available_balance_euros',
			'sdsp': 'available_balance_currency',
		}
		conversions = {
			'ldd':deserialize_money,
			'ldde':deserialize_money,
			'scne':deserialize_money,
			'scnt':deserialize_money,
			'sdse':deserialize_money,
			'sdsp':deserialize_money,
		}
		return populate_object_from_mapping_and_conversions(Balance(), balance_movements_slds, mapping, conversions)

	@classmethod
	def from_account_details_balance(cls, details_slds):
		mapping = {
			'acb': 'awaiting_charge',
			'ctv': 'captive_amount',
			'moe': 'currency',
			'ldd': 'available_overdraft',
			'ldde': 'available_overdraft_euros',
			'ldn': 'negotiated_overdraft', 
			'ldu': 'available_overdraft',
			'scne': 'balance_euros',
			'scnt': 'balance_currency',
			'sdse': 'available_balance_euros',
			'sdsp': 'available_balance_currency',
			'ti': 'unavailable_amount',
		}
		conversions = {
			'acb': deserialize_money,
			'ctv': deserialize_money,
			'ldd': deserialize_money,
			'ldde': deserialize_money,
			'ldn': deserialize_money,
			'ldu': deserialize_money,
			'scne': deserialize_money,
			'scnt': deserialize_money,
			'sdse': deserialize_money,
			'sdsp': deserialize_money,
			'ti': deserialize_money,
		}
		return populate_object_from_mapping_and_conversions(Balance(), details_slds, mapping, conversions)


class Account:
	@classmethod
	def from_auth_result(cls, auth_result_lcnt):
		mapping = {
			'des':'description',
			'key':'key',
			'nc':'account_number',
			'tc':'account_type'
		}
		account = Account()
		account.transactions = []
		return populate_object_from_mapping_and_conversions(account, auth_result_lcnt, mapping)

class CgdSession:
	def __init__(self, userid, password):
		self._s = create_requests_session()
		self._auth = (userid, password)

	def login(self):
		auth_response = self._s.get(Urls.authentication(self._auth[0]), auth = self._auth)
		if auth_response.status_code != 200:
			message = auth_response.content
			try:
				message = auth_response.json["m"]
			except:
				pass
			raise CgdCommunicationException("Authentication failed: " + message)
		if not auth_response.json.has_key("lcnt"):
			raise CgdCommunicationException("Missing key 'lcnt' in authentication response")
		self.known_accounts = { account.key : account for account in [Account.from_auth_result(account_json) for account_json in auth_response.json['lcnt']]}

	def load_account_balance(self, account_key):
		if not self.known_accounts.has_key(account_key):
			# we can avoid this when we figure out a way to just load the account info
			# so far this is always a side effect of loading something else
			raise InternalCgdException("Account key %s wasn't a known account" % account_key)

		response = self._s.get(Urls.account_balance(account_key))
		account = self.known_accounts[account_key]

		account.balance = Balance.from_balance_movements(response.json["slds"])
		return account.balance

	def load_latest_transactions(self, account_key, page_size = 30, first_movement_number = -1):
		response = self._s.get(Urls.account_details(account_key))

		for lcnt in response.json["lcnt"]:
			possible_new_account = Account.from_auth_result(lcnt)
			if not self.known_accounts.has_key(possible_new_account.key):
				self.known_accounts[possible_new_account.key] = possible_new_account

		account = self.known_accounts[account_key]
		account.balance = Balance.from_account_details_balance(response.json["slds"])

		transactions_bag = list(Transaction.from_account_details_transactions(lmov) for lmov in response.json["lmov"])

		page_key = response.json["pkl"]
		while(len(transactions_bag) <= page_size and min(t.movement_number for t in transactions_bag) > first_movement_number):
			until = datetime.strptime(page_key[1], "%Y-%m-%d")
			more_details_response = self._grab_more_details(self._s, account_key, until-timedelta(days = 30), until, page_key)
			if not more_details_response.json.has_key("lmov") or len(more_details_response.json["lmov"]) == 0:
				break
			page_key = response.json["pkl"]
			transactions_bag.extend(Transaction.from_account_details_transactions(lmov) for lmov in more_details_response.json["lmov"])

		seen = set()
		account.transactions_bag = transactions_bag
		account.transactions.extend(t for t in transactions_bag if t.movement_number not in seen and not seen.add(t.movement_number))

	def _grab_more_details(self, s, account_key, _from, until, page_key):
		data = {
			'cnt':account_key,
			'dtf':serialize_date(until),
			'dti':serialize_date(_from),
			'pkl':page_key
		}
		headers = {'Content-Type': 'application/json', 'Expect':'100-continue'}
		return s.post(Urls.account_more_details(), data=json.dumps(data), headers = headers)
