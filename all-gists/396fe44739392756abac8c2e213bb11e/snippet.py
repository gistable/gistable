#!/usr/bin/env python
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import binascii
from decimal import Decimal

try:
	from trezorlib.client import TrezorClient
	from trezorlib.transport_hid import HidTransport
	from trezorlib.tx_api import TxApiInsight
	from trezorlib import types_pb2 as types
	
	# patch trezorlib TxApiInsight to send txhashes across as plaintext string (instead of bytes) when using python3
	class pt_TxApiInsight(TxApiInsight):
		def get_tx(self, txhash):
			if type(txhash) is bytes:
				txhash = txhash.decode('utf-8')
			return super(pt_TxApiInsight, self).get_tx(txhash)
	TxApiBitcoin = pt_TxApiInsight(network='insight_bitcoin', url='https://insight.bitpay.com/api/')
except ImportError:
	print('Error importing trezorlib, install it with: pip install trezor')
	sys.exit(0)

import logging
from logging.handlers import RotatingFileHandler
worklog = logging.getLogger('sign_trezor_tx')
#shandler = logging.handlers.RotatingFileHandler('sign_trezor_tx.log', maxBytes=1024*1024*10, backupCount=1000)
shandler = logging.StreamHandler(sys.stdout)
worklog.setLevel(logging.DEBUG)
worklog.addHandler(shandler)
shandler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', '%Y/%m/%d %H:%M:%S'))

try:
	input = raw_input
except NameError:
	pass

ADDRESS_TO_SWEEP_PATH = "44'/0'/0'/0/1"
ASSET_TO_SWEEP = 'EBEX'
ASSET_QUANTITY = Decimal('1') # amount of ASSET_TO_SWEEP to send, the script will convert to satoshis if ASSET_DIVISIBLE is True
ASSET_DIVISIBLE = False # whether ASSET_TO_SWEEP is divisible
OUTPUT_ADDRESS = '1QEx9kdYQqmNzC8HW8FPQS3Mb7vVXYa7bK' # address where ASSET_TO_SWEEP is to be sent
TX_FEE = 7666 # static transaction fee to be paid for the tx, in satoshis -- set to 0 to have counterpary-lib auto calculate
BITCOIN_USER = ''
BITCOIN_PW = ''
BITCOIN_URL = '127.0.0.1'
BITCOIN_PORT = '8332'

COUNTERPARTY_URL = 'http://127.0.0.1:4000'
COUNTERPARTY_USER = ''
COUNTERPARTY_PW = ''

def formatted(x):
	return format(Decimal(x).quantize(Decimal('1.00000000')), ',.8f').strip('0').rstrip('.')

def to_satoshis(x):
	return int((Decimal(x) * Decimal(1e8)).quantize(Decimal('1.00000000')))

def from_satoshis(x):
	return (Decimal(x) / Decimal(1e8)).quantize(Decimal('1.00000000'))

def bitcoin_(method, *args):
	service_url = 'http://{}:{}@{}:{}'.format(BITCOIN_USER, BITCOIN_PW, BITCOIN_URL, BITCOIN_PORT)
	js = requests.post(
		service_url, headers={'content-type': 'application/json'}, verify=False, timeout=60, data=json.dumps({
			'method': method, 'params': args, 'jsonrpc': '2.0'
		})
	)
	return js.json()

def counterparty(payload, tojson=True):
	xcp_url = '{}/api/'.format(COUNTERPARTY_URL)
	xcp_auth = HTTPBasicAuth(COUNTERPARTY_USER, COUNTERPARTY_PW)
	try:
		headers = {'content-type': 'application/json'}
		if 'jsonrpc' not in payload.keys():
			payload['jsonrpc'] = '2.0'
		if 'id' not in payload.keys():
			payload['id'] = 0
		
		response = requests.post(
			xcp_url, data=json.dumps(payload), headers=headers, auth=xcp_auth, 
			timeout=15, verify=False
		)
		if tojson:
			resp = response.json()
			if 'error' in resp.keys():
				worklog.error('Error making request: {}'.format(resp['error']))
			return resp['result']
		return response
	except Exception as e:
		worklog.exception('Exception making cp request: {}'.format(e))
		return None
	
def create_cp_tx(source, destination, asset, qty, divisible, fee=None):
	payload = {
		'method': 'create_send', 'params': {
			'source': source, 'destination': destination,
			'asset': asset, 'quantity': int(qty) if not divisible else to_satoshis(qty),
			#'encoding': 'auto',
			'encoding': 'opreturn', # only OP_RETURN transactions currently supported
			'allow_unconfirmed_inputs': True
		}
	}
	if fee is not None:
		payload['params']['fee'] = fee
	
	return counterparty(payload)

def get_trezor_client():
	devices = HidTransport.enumerate()
	if len(devices) == 0:
		worklog.error('could not find any trezor device connected')
		return None
	
	transport = HidTransport(devices[0])
	client = TrezorClient(transport)
	return client

if __name__ == '__main__':
	inputs = []
	outputs = []
	tzcl = get_trezor_client()
	if not tzcl:
		worklog.error('Failed to get trezor device, aborting.')
		sys.exit(0)
	tzcl.set_tx_api(TxApiBitcoin)
	
	bip32_path = tzcl.expand_path(ADDRESS_TO_SWEEP_PATH)
	address = tzcl.get_address('Bitcoin', bip32_path)
	worklog.info('Attempting to send {} {} out of {}'.format(str(ASSET_QUANTITY), ASSET_TO_SWEEP, address))
	utx = create_cp_tx(address, OUTPUT_ADDRESS, ASSET_TO_SWEEP, ASSET_QUANTITY, ASSET_DIVISIBLE, fee=TX_FEE)
	worklog.info('Create transaction: {}'.format(utx))
	
	decoded = bitcoin_('decoderawtransaction', utx)['result']
	for vin in decoded['vin']:
		inputs.append(types.TxInputType(
			prev_hash = binascii.unhexlify(vin['txid']),
			prev_index = int(vin['vout']),
			address_n = tzcl.expand_path(ADDRESS_TO_SWEEP_PATH)
		))
	for vout in decoded['vout']:
		if vout['scriptPubKey']['type'] in ['nulldata']:
			outputs.append(types.TxOutputType(
				amount = to_satoshis( vout['value'] ),
				script_type = types.PAYTOOPRETURN,
				op_return_data = binascii.unhexlify(vout['scriptPubKey']['hex'][4:])
			))
		elif vout['scriptPubKey']['type'] in ['pubkeyhash']:
			outputs.append(types.TxOutputType(
				amount = to_satoshis( vout['value'] ),
				script_type = types.PAYTOADDRESS,
				address = vout['scriptPubKey']['addresses'][0]
			))
		else:
			worklog.error('No code written to handle vout of type {}'.format(vout['scriptPubKey']['type']))
			tzcl.close()
			sys.exit(0)
	
	worklog.info('\n\nSigning Transaction (Check your trezor for input) ...\n')
	sigs, stx = tzcl.sign_tx('Bitcoin', inputs, outputs)
	stx = binascii.hexlify(stx).decode('utf-8')
	worklog.info('\nstx: {}'.format(stx))
	
	inp = input('\nbroadcast TX (y/n)?\n-> ')
	if inp.lower() in ['y', 'yes', 'yeah', 'sure']:
		tx = bitcoin_('sendrawtransaction', stx)
		if not tx['result']:
			worklog.error('Error sending:\n{}'.format(tx))
		else:
			worklog.info('\n\nSent TX: {}'.format(tx['result']))
	else:
		worklog.info('Not broadcasting tx')
	
	tzcl.close()
	sys.exit(0)