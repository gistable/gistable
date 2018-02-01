#!/usr/bin/env python
import hashlib
import hmac
import time
import requests
import datetime

# Q. Do you have A Websocket API?
# A. Yes, and we strongly recommend you to use it. Please, check our JavaScript websocket implementation for our WebSocket API here:
# https://github.com/blinktrade/frontend/blob/master/jsdev/bitex/api/bitex.js
#
# Q. Where is the public API for orderbook and ticker data?
# A. https://api.blinktrade.com/api/v1/{CURRENCY_CODE}/ticker
#    https://api.blinktrade.com/api/v1/{CURRENCY_CODE}/orderbook
#    https://api.blinktrade.com/api/v1/{CURRENCY_CODE}/trades
#  Where {CURRENCY_CODE} is:
#      BRL for Brazil Reals - FoxBit
#      VEF for Venezuelan Bolivares - SurBitcoin
#      CLP for Chilean Pesos - ChileBit.NET
#      VND for Vietnamise Dongs - VBTC
#      PKR for Pakistani Ruppe - UrduBit
#
#
# Q. What about the Trade API and their respective api endpoints for test and production? 
# testnet -> https://api.testnet.blinktrade.com/tapi/v1/message
# prod -> https://api.blinktrade.com/tapi/v1/message

# Q. How to generate an api key ?
# 1. go to your exchange account 
#    https://tesnet.blinktrade.com/ for testnet environment
# 2. signup 
# 3. Go to API 
# 4. Select a name and all the permissions for that API Key.
# 5. Get the API Key and API Secret.  The API Secret will only be shown once.   The API Password is only used in the WebSocket Api

# Q. Can I use the same API in all exchanges powered by Blinktrade? 
# A. Yes, same exactly API. You only have to change the BrokerID field
#    *--------------*----*
#    | BrokerID     | ID |
#    *--------------*----*
#    | SurBitcoin   |  1 |
#    | VBTC         |  3 |
#    | FoxBit       |  4 |
#    | Testnet      |  5 |
#    | UrduBit      |  8 |
#    | ChileBit     |  9 |
#    *--------------*----*


# Q. How does the api works ?
# A. Though the blinktrade API, you can 
#    - Send and cancel orders
#    - Get a list of your open orders
#    - Get your balance
#    - Generate a Bitcoin deposit address

# Q. Can I generate a withdrawal request? 
# A. Not through the web api.  You should use our Websocket API for that. 

#Curl Example:
#apiKey=YOUR_API_KEY_GENERATED_IN_API_MODULE
#secret=YOUR_SECRET_KEY_GENERATED_IN_API_MODULE
#timestamp=`date +%s`
#signature=`echo -n $timestamp | openssl dgst -sha256 -hex -hmac $secret |  awk '{print $2}'`
#curl -XPOST  https://api.testnet.blinktrade.com/tapi/v1/message -H "Nonce:$timestamp" -H "APIKey:$apiKey" -H "Content-Type:application/json" -H "Signature:$signature" -d '{"MsgType":"U2","BalanceReqID":1}'

def send_msg(msg, env='prod'):
    if env == 'prod':
        BLINKTRADE_API_URL = 'https://api.blinktrade.com'
    else:
        BLINKTRADE_API_URL = 'https://api.testnet.blinktrade.com'
    BLINKTRADE_API_VERSION = 'v1'
    TIMEOUT_IN_SECONDS = 10

    key = 'YOUR_API_KEY_GENERATED_IN_API_MODULE'
    secret = 'YOUR_SECRET_KEY_GENERATED_IN_API_MODULE'

    dt = datetime.datetime.now()
    nonce = str(int((time.mktime( dt.timetuple() )  + dt.microsecond/1000000.0) * 1000000))
    signature = hmac.new( secret,  nonce, digestmod=hashlib.sha256).hexdigest()

    headers = {
        'user-agent': 'blinktrade_tools/0.1',
        'Content-Type': 'application/json',         # You must POST a JSON message
        'APIKey': key,                              # Your APIKey
        'Nonce': nonce,                             # The nonce must be an integer, always greater than the previous one. 
        'Signature': signature                      # Use the API Secret  to sign the nonce using HMAC_SHA256 algo
    }
    url = '%s/tapi/%s/message' % (BLINKTRADE_API_URL, BLINKTRADE_API_VERSION)
    return requests.post(url, json=msg, verify=True, headers=headers).json()


# Request Balance 
msg = { 
    "MsgType": "U2",    # Balance Request
    "BalanceReqID": 1   # An ID assigned by you. It can be any number.  The response message associated with this request will contain the same ID.
}
print send_msg(msg)
# {
#   "Status": 200,        # 200 for OK, 4xx for errors
#   "Description": "OK",  # Ok if successful, or an error description 
#   "Responses": [        # An array of all responses.  Some messages might generated more than one response. 
#                   {
#                       "MsgType": "U3",            # Balance response 
#                       "5": {                      # 5 stands for your balance with the BrokerID number 5
#                           "BTC": 1985787956019,   # Amount in satoshis of BTC you have deposited into your account 
#                           "BTC_locked": 0,        # Amount in satoshis of BTC you have locked ( open orders, margin positions, etc... )
#                           "USD": 41562916193320,  # Amount in satoshis of USD( or your FIAT currency) you have deposited into your account  
#                           "USD_locked": 0         # Amount in satoshis of USD( or your FIAT currency) you have locked ( open orders, margin positions, etc... )
#                       }, 
#                       "ClientID": 90800003,       # Your account ID
#                       "BalanceReqID": 1           # This should match the BalanceReqID sent on the message U2
#                   }
#               ]
# }


# Request Open Orders 
msg = {
    "MsgType": "U4",
    "OrdersReqID": 1,
    "Page": 0,
    "PageSize": 100,
    "Filter":["has_leaves_qty eq 1"]  # Set it to "has_leaves_qty eq 1" to get open orders, "has_cum_qty eq 1" to get executed orders, "has_cxl_qty eq 1" to get cancelled orders
}
print send_msg(msg)
#{
#   "Status": 200, 
#   "Description": "OK", 
#   "Responses": [
#                   {
#                       "MsgType": "U5",        # Order list response
#                       "OrdersReqID": 1,       # Match the request OrdersReqID field.
#                       "Page": 0,              # Starts with 0.
#                       "PageSize": 100,        # The page size. If the length of the array OrdListGrp is greather or equal to the PageSize, you should issue a new request incrementing the Page
#                       "OrdListGrp": [],       # Array of all orders.  
#                       "Columns": [            # Description of all columns of the all orders in OrdListGrp
#                                   "ClOrdID",   # client order id. Set by you.
#                                   "OrderID",   # Order id. Set by blinktrade 
#                                   "CumQty",    # The executed quantity of this order
#                                   "OrdStatus", # 0=New, 1=Partially filled, 2=Filled, 4=Cancelled, 8=Rejected, A=Pending New
#                                   "LeavesQty", # Quantity open for further execution
#                                   "CxlQty",    # Total quantity canceled for this order.
#                                   "AvgPx",     # Calculated average price of all fills on this order.
#                                   "Symbol",    # BTCUSD, BTCBRL 
#                                   "Side",      # 1=Buy, 2=Sell, E=Redem, F=Lend, G=Borrow
#                                   "OrdType",   # 1=Market, 2=Limited, 3=Stop, 4=Stop Limit, G=Swap, P=Pegged
#                                   "OrderQty",  # Quantity ordered in satoshis
#                                   "Price",     # Price per unit in satoshis
#                                   "OrderDate", # Order date in UTC 
#                                   "Volume",    # Quantity * Price 
#                                   "TimeInForce"# 0=Day, 1=Good Till Cancel, 4=Fill or Kill
#                        ]
#                   }
#               ]
# }



# Send a new order 
client_order_id = str(int(time.time()))  # this ID must be uniq
msg = {
    "MsgType":"D",              # New Order Single message. Check for a full doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_D_68.html 
    "ClOrdID": client_order_id, # Unique identifier for Order as assigned by you
    "Symbol":"BTCUSD",          # Can be BTCBRL, BTCPKR, BTCVND, BTCVEF, BTCCLP.
    "Side":"1",                 # 1 - Buy, 2-Sell
    "OrdType":"2",              # 2 - Limited order 
    "Price":26381000000,        # Price in satoshis 
    "OrderQty":2723810,         # Qty in saothis 
    "BrokerID":5                # 1=SurBitcoin, 3=VBTC, 4=FoxBit, 5=Tests , 8=UrduBit, 9=ChileBit
}
print send_msg(msg)
# {
#   "Status": 200, 
#   "Description": "OK", 
#   "Responses": [  # In this example, the request returned 2 messages.
#                   {
#                       "MsgType": "U3",                    # Balance respose. Problably because the request also change your account balance.
#                       "5": {"USD_locked": 718568316},     # In this example, modified the amount of USD you have locked into your account.
#                       "ClientID": 90800003                # Your account ID
#                   }, 
#                   {
#                       "MsgType": "8",             # Execution Report. Check for a full fix doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_8_8.html
#                       "OrderID": 5669865,         # Unique identifier for Order as assigned by broker
#                       "ExecID": 35,               # Unique identifier of execution message as assigned by broker
#                       "ExecType": "0",            # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New 
#                       "OrdStatus": "0",           # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New 
#                       "LeavesQty": 2723810,       # Quantity open for further execution
#                       "Symbol": "BTCUSD",         # Pair
#                       "OrderQty": 2723810,        # Quantity ordered in satoshis
#                       "LastShares": 0,            # Quantity of shares bought/sold on this fill
#                       "LastPx": 0,                # Price of the last fill
#                       "CxlQty": 0,                # Total quantity canceled for this order.
#                       "TimeInForce": "1",         # 0=Day, 1=Good Till Cancel, 4=Fill or Kill
#                       "CumQty": 0,                # Total quantity filled
#                       "ClOrdID": "1440927610",    # Unique identifier for Order as assigned by you
#                       "OrdType": "2",             # 1=Market, 2=Limited, 3=Stop, 4=Stop Limit, G=Swap, P=Pegged
#                       "Side": "1",                # 1=Buy, 2=Sell, E=Redem, F=Lend, G=Borrow
#                       "Price": 26381000000,       # Price per unit of quantity in satoshis
#                       "ExecSide": "1",            # Side of this fill 
#                       "AvgPx": 0                  # Calculated average price of all fills on this order.
#                   }
#               ]
# }


# Cancel the order sent in the previous step 
msg = {
    "MsgType":"F",                  # Order Cancel Request message. Check for a full doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_F_70.html 
    "ClOrdID": client_order_id      # Unique identifier for Order as assigned by you
}
print send_msg(msg)
# The response of Cancel Order Request is almost identical to the New Order Single, but with different paramenters.
# {
#   "Status": 200, 
#   "Description": "OK", 
#   "Responses": [
#                   {
#                       "MsgType": "U3",            # Balance respose. Problably because the request also change your account balance.
#                       "5": {"USD_locked": 0},     # In this example, modified the amount of USD you have locked into your account.
#                       "ClientID": 90800003        # Your account ID
#                   }, 
#                   {
#                       "MsgType": "8",             # Execution Report. Check for a full fix doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_8_8.html
#                       "OrderID": 5669865,         # Unique identifier for Order as assigned by broker
#                       "ExecID": 36,               # Unique identifier of execution message as assigned by broker
#                       "ExecType": "4",            # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New 
#                       "OrdStatus": "4",           # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New 
#                       "LeavesQty": 0,             # Quantity open for further execution
#                       "Symbol": "BTCUSD",         # Pair
#                       "OrderQty": 2723810,        # Quantity ordered in satoshis
#                       "LastShares": 0,            # Quantity of shares bought/sold on this fill
#                       "LastPx": 0,                # Price of the last fill
#                       "CxlQty": 2723810,          # Total quantity canceled for this order.
#                       "TimeInForce": "1",         # 0=Day, 1=Good Till Cancel, 4=Fill or Kill
#                       "CumQty": 0,                # Total quantity filled
#                       "ClOrdID": "1440927610",    # Unique identifier for Order as assigned by you
#                       "OrdType": "2",             # 1=Market, 2=Limited, 3=Stop, 4=Stop Limit, G=Swap, P=Pegged
#                       "Side": "1",                # 1=Buy, 2=Sell, E=Redem, F=Lend, G=Borrow 
#                       "Price": 26381000000,       # Price per unit of quantity in satoshis
#                       "ExecSide": "1",            # Side of this fill 
#                       "AvgPx": 0                  # Calculated average price of all fills on this order.
#                   }
#               ]
#  }


# Generating a bitcoin deposit address  
 msg = {
    "MsgType":"U18",    # Deposit request 
    "DepositReqID":1,   # Deposit Request ID. 
    "Currency":"BTC",   # Currency. 
    "BrokerID": 5       # Exchange ID
}
print send_msg(msg)
# {
#    "Status": 200, 
#    "Description": "OK", 
#    "Responses": [
#                   {
#                       "DepositReqID": 1,                                  # Deposit Request ID
#                       "MsgType": "U19",                                   # Deposit response 
#                       "DepositMethodID": null,                            # Deposit Method ID
#                       "DepositMethodName": "deposit_btc",                 # Deposit method name
#                       "DepositID": "12db13d5c36c436993f8e8156467d2b6",    # Deposit ID
#                       "UserID": 90800003,                                 # Your account ID
#                       "ControlNumber": null,                              # Control number. Only used for FIAT deposits 
#                       "Type": "CRY",                                      # CRY = Crypto Currency 
#                       "Username": "rodrigo",                              # Your username 
#                       "AccountID": 90800003,                              # Account ID
#                       "Data": {
#                           "InputAddress": "mzUfpURjD1hDPNk7QBWQkXN5NbKjpf6e56",   # The address that you have to deposit 
#                           "Destination": "mtzsTx923NqnFeHugUBsgQKqr8YkEtzQzU"     # This is the exchange wallet. DO NOT DEPOSIT IN THIS ADDRESS.
#                       }, 
#                       "ClOrdID": null,                                    # Unique identifier for Order as assigned by you
#                       "Status": "0",                                      # 0 - New 
#                       "Created": "2015-08-31 05:39:31",                   # Creation date GMT
#                       "BrokerID": 5,                                      # Exchange ID
#                       "Value": 0,                                         # Amount
#                       "PaidValue": 0,                                     # Paid amount 
#                       "Currency": "BTC",                                  # Currency
#                       "ReasonID": null,                                   # Reason for the rejection - ID
#                       "Reason": null,                                     # Reason for the rejection - Description
#                       "PercentFee": 0.0,                                  # Percent fee to process this deposit 
#                       "FixedFee": 0                                       # Fixed fee in satoshis 
#                   }, 
#               ]
# }

# Request a FIAT deposit
 msg = {
    "MsgType":"U18",    # Deposit request 
    "DepositReqID":1,   # Deposit Request ID. 
	"DepositMethodID":403, # Deposit Method ID - Check with your exchange. 
	"Value":150000000000, # Amount in satoshis
    "Currency":"BRL",   # Currency. 
    "BrokerID": 5       # Exchange ID
}
print send_msg(msg)
# {
#   'Status': 200, 
#   'Description': 
#   'OK', 
#   'Responses': [
#                   {
#                        'MsgType': u'U19', 
#                        'DepositMethodName': u'bb', 
#                        'UserID': 90800025, 
#                        'ControlNumber': 402000057, 
#                        'State': u'UNCONFIRMED', 
#                        'Type': u'DTP', 
#                        'AccountID': 90800025, 
#                        'Username': u'rodrigo', 
#                        'CreditProvided': 0, 
#                        'DepositReqID': 6000745, 
#                        'DepositID': u'a637e243382f4b768b5faccb97878ab3', 
#                        'Reason': None, 
#                        'PercentFee': 0.0, 
#                        'Data': {}, 
#                        'ClOrdID': None, 
#                        'Status': '0', 
#                        'Created': '2016-03-28 20:28:02', 
#                        'DepositMethodID': 403, 
#                        'Value': 150000000000, 
#                        'BrokerID': 4, 
#                        'PaidValue': 0, 
#                        'Currency': u'BRL', 
#                        'ReasonID': None, 
#                        'FixedFee': 0
#                   }
#                ]
# }

# Request a Bitcoin Withdrawal 
msg = {
 "MsgType": 'U6',
 "WithdrawReqID": 617625,    # Request ID.  
 "Method": 'bitcoin',        # bitcoin for BTC. Check with the exchange all available withdrawal methods  
 "Amount": 3000000,          # Amount in satoshis 
 "Currency": 'BTC',          # Currency 
 "Data": {
    "Wallet":"mwmabpJVisvti3WEP5vhFRtn3yqHRD9KNP"  # Your Wallet 
 }
}
print send_msg(msg)
#  "Status": 200,
#  "Description": "OK",
#  "Responses": [
#                 {
#                     "MsgType": "U7",            # Withdrawal Response
#                     "WithdrawReqID": 617625,    # Withdraw Request ID
#                     "WithdrawID": 339,          # Withdraw ID. You should keep this number in case you want to cancel the Withdraw request
#                     "UserID": 90800025,         # Your account ID
#                     "Username": "rodrigo",      # Your username
#                     "Method": "bitcoin",        # Bitcoin method
#                     "Amount": 3000000,          # Requested Amount
#                     "BrokerID": 4,              # Exchange ID
#                     "ClOrdID": None,            # Unique identifier for Order as assigned by you
#                     "Created": "2016-03-21 08:27:45",   # Creation date GMT
#                     "Currency": "BTC",          # Currency
#                     "Data": {
#                             "Wallet": "mwmabpJVisvti3WEP5vhFRtn3yqHRD9KNP"    # Wallet Address
#                     },
#                     "FixedFee": 10000,          # Fixed portion of the Fee in satoshis
#                     "PercentFee": 0.0,          # Percent portion of the fee
#                     "PaidAmount": 3010000,      # The amount + fees that was deducted from the account
#                     "Reason": null,             # Reason for the rejection - Description
#                     "ReasonID": null,           # Reason for the rejection - ID
#                     "Status": u'1'              # 0-Unconfirmed ( In this case, you must confirm withdrawal using a second factor of authentication ),
#                                                   1-Pending,
#                                                   2-In Progress,
#                                                   4-Completed,
#                                                   8-Cancelled
#                 },
#                 {
#                     "MsgType": "U3",            # Balance response. Withdrawal requests might change your balance 
#                     "4": {"BTC": 2087629545},   # In this example, your BTC balance have changed
#                     "ClientID": 90800025        # Your account ID
#                 }
#               ],
#  }


# Request a FIAT Witdrawal 
msg = {
  "MsgType": 'U6',
  "WithdrawReqID": 382616,
  "Method": 'bradesco',  # Method. 
  "Currency": 'BRL',
  "Amount": 1500000000,
  "Data": {
    "AccountBranch":"111",
    "AccountNumber":"4444-5",
    "AccountType":"corrente", 
    "CPF_CNPJ":"00000000000"
  },
}
# See the response for Bitcoin Withdrawal 
# Check with the exchange all the methods and required fields in the Data field.
# *------------*----------------------*------------------------------------------------------------------------*
# |Exchange    |Methods               | Required Data fields                                                   |
# *------------|----------------------*------------------------------------------------------------------------*
# |3-VBTC      |banktransfer          | BankName,AccountBranch,BankCity,AccountName,AccountNumber,BankSwift    |
# |3-VBTC      |VPBankinternaltransfer| VPbankbranch,BankCity,AccountName,AccountNumber,BankSwift              |
# |3-VBTC      |cashtoID              | BankName,BankBranch,BankCity,Clientname,ClientIDNr,Issue Date ID,Place of Issue,Phone Number of Recipient|
# *------------*----------------------*------------------------------------------------------------------------* 
# |4-FOXBIT    |bradesco              | AccountBranch, AccountNumber, AccountType, CPF_CNPJ                    |
# |4-FOXBIT    |bb                    | AccountBranch, AccountNumber, AccountType, CPF_CNPJ                    |
# |4-FOXBIT    |Caixa                 | AccountBranch, AccountNumber, AccountType, CPF_CNPJ                    |
# |4-FOXBIT    |ted                   | BankName,BankNumber,AccountBranch,AccountNumber,AccountType,CPF_CNPJ   |
# *------------*----------------------*------------------------------------------------------------------------* 
# |9-CHILEBIT  |banktransfer          | BankName,AccountType,AccountNumber,AccountName,RUT,Email               |
# *------------*----------------------*------------------------------------------------------------------------* 
# |8-URDUBIT   |SCB2SCB               | AccountName,AccountNumber                                              |
# |8-URDUBIT   |Check                 | NameOnAccount,AccountNo,City,BankName                                  |
# |8-URDUBIT   |HBL                   | AccountName,AccountNumber                                              |
# |8-URDUBIT   | AlliedBank           | AccountName,AccountNumber                                              |
# |8-URDUBIT   | BankIslami           | AccountName,AccountNumber                                              |
# |8-URDUBIT   | BankAlfalah          | AccountName,AccountNumber                                              |
# |8-URDUBIT   | Other                | Name,AccountNumber,BankName,CNIC,Mobile,Address                        | 
# |8-URDUBIT   | SKMCH                | Cellphone                                                              | 
# |8-URDUBIT   | MeezanBank           | AccountName,AccountNumber                                              |
# |8-URDUBIT   | EasypaisaMobile      | MobileAccount                                                          |
# |8-URDUBIT   | JSBankCOC            | Name,Cell,CNIC                                                         |
# |8-URDUBIT   | JSBank               | Name,Account,PhoneNumber                                               |
# *------------*----------------------*------------------------------------------------------------------------* 

# Request a list of all your withdrawals 
msg = {
    'MsgType': 'U26',         
    'WithdrawListReqID': 1,    # WithdrawList Request ID
    'Page': 0,  
    'PageSize': 100,
    'StatusList': ['1', '2']   # 1-Pending, 2-In Progress, 4-Completed, 8-Cancelled 
  };
print send_msg(msg)
# {
#    "Status": 200, 
#    "Description": "OK", 
#    "Responses": [
#                   {
#                      "MsgType": "U27",              # Withdrawal List Response Type
#                      "WithdrawListReqID": 9269169,  # WithdrawList Request ID
#                      "Page": 0,                     # Page number
#                      "PageSize": 100,               # Page size - Max of 100
#                      "Columns": [                   # Column
#                        "WithdrawID",                # Withdrawal ID 
#                        "Method",                    # Withdrawal Method 
#                        "Currency",                  # Currency 
#                        "Amount",                    # Amount requested
#                        "Data",                      # Data associated with the withdrawal 
#                        "Created",                   # Creation date
#                        "Status",                    # Status - 1-Pending, 2-In Progress, 4-Completed, 8-Cancelled 
#                        "ReasonID",                  # Cancellation Reason ID 
#                        "Reason",                    # Cancellation Reason description    
#                        "PercentFee",                # Fee in % charged for this operation 
#                        "FixedFee",                  # Fixe Fee charged for this operation 
#                        "PaidAmount",                # Amount paid    
#                        "UserID",                    # Account ID
#                        "Username",                  # Account Username 
#                        "BrokerID",                  # Exchange ID
#                        "ClOrdID"                    # Unique identifier for Order as assigned by you
#                      ],
#                      "WithdrawListGrp": [           # Response array containing all withdrawals
#                        [
#                          73578,
#                          "bitcoin", 
#                          "BTC", 
#                          300000000, 
#                          {
#                             "Currency": "BTC", 
#                              "TransactionID": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 
#                              "Fees": "\u0e3f 0,00010000", 
#                              "Instant": "NO", 
#                              "Wallet": "1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#                          }, 
#                         "2016-01-16 18:45:39", 
#                         "4",
#                         null, 
#                         null, 
#                         0.0, 
#                         10000, 
#                         300010000, 
#                         90800480, 
#                         "yourusername", 
#                         4, 
#                         null ],
#                      ] 
#                    }
#    ]
# }
