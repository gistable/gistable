#!/usr/bin/env python

import sys
import datetime
import time
from datetime import timedelta

sys.path.append('/home/reb/local/azure-sdk-for-python/')

from  azure.storage import *
from azure.storage.sharedaccesssignature import *

blob_service1 = BlobService(account_name='account1', account_key='key1')
blob_service2 = BlobService(account_name='account2', account_key='key2')

def format_date_time (t):
	return t.strftime('%Y-%m-%dT%H:%M:%SZ')

def sign (blob_service, container_name, blob_name):
	sas = SharedAccessSignature(account_name=blob_service.account_name, account_key=blob_service.account_key)

	start = datetime.now()
	expiry = start + timedelta(minutes = 10)

	accss_plcy = AccessPolicy()
	accss_plcy.start = format_date_time (start)
	accss_plcy.expiry = format_date_time (expiry)
	accss_plcy.permission = 'r'
	sap = SharedAccessPolicy(accss_plcy)

	qry_str = sas.generate_signed_query_string(container_name + '/' + blob_name,  RESOURCE_BLOB,  sap)
	qry_str2 =  sas._convert_query_string(qry_str)
	return blob_service.protocol + '://' + blob_service._get_host() + '/' + container_name + '/' + blob_name + '?' + qry_str2



# copy from source to destination

source = sign(blob_service2, 'junk', 'foo.txt')


blob_service1.copy_blob('foo', 'foo3.txt', source)