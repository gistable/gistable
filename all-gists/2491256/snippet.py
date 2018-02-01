import urllib
import urlparse
import collections
import httplib

def TestPayment():
#Set our headers
    headers = {
        'X-PAYPAL-SECURITY-USERID': 'jb-us-seller_api1.paypal.com',
        'X-PAYPAL-SECURITY-PASSWORD': 'WX4WTU3S8MY44S7F',
        'X-PAYPAL-SECURITY-SIGNATURE': 'AFcWxV21C7fd0v3bYYYRCpSSRl31A7yDhhsPUU2XhtMoZXsWHFxu-RWy',
        'X-PAYPAL-APPLICATION-ID': 'APP-80W284485P519543T',
        'X-PAYPAL-SERVICE-VERSION':'1.1.0',
        'X-PAYPAL-REQUEST-DATA-FORMAT':'NV',
        'X-PAYPAL-RESPONSE-DATA-FORMAT':'NV'
    }

    ###################################################################
    # In the above $headers declaration, the USERID, PASSWORD and 
    # SIGNATURE need to be replaced with your own.
    ################################################################### 

    #Set our POST Parameters
    params = collections.OrderedDict()
    params['requestEnvelope.errorLanguage'] = 'en_US';
    params['requestEnvelope.detailLevel'] = 'ReturnAll';
    params['reverseAllParallelPaymentsOnError'] = 'true';
    params['returnUrl'] = 'https://apps.facebook.com/XXXXXXXX/payaccept';
    params['cancelUrl'] = 'https://apps.facebook.com/XXXXXXXX/paycancel';
    params['actionType'] = 'PAY';
    params['currencyCode'] = 'USD';
    params['feesPayer'] = 'EACHRECEIVER';
    params['receiverList.receiver(0).email'] = 'platfo_1255612361_per@gmail.com';
    params['receiverList.receiver(0).amount'] = '10.00';
    params['receiverList.receiver(1).email'] = 'enduser_biz@gmail.com';
    params['receiverList.receiver(1).amount'] = '20.00';

    #Add Client Details

    params['clientDetails.ipAddress'] = '127.0.0.1';
    params['clientDetails.deviceId'] = 'mydevice';
    params['clientDetails.applicationId'] = 'PayNvpDemo';


    enc_params = urllib.urlencode(params)
    print ("*****************")
    print (enc_params)
    print ("*****************")

    #Connect to sand box and POST.
    conn = httplib.HTTPSConnection("svcs.sandbox.paypal.com")
    conn.request("POST", "/AdaptivePayments/Pay/", enc_params, headers)

    print ("*****************")
    #Check the response - should be 200 OK.
    response = conn.getresponse()
    print (response.status, response.reason)
    print ("*****************")

    #Get the reply and print it out.
    data = response.read()
    print (urlparse.parse_qs(data))
    print ("*****************")

TestPayment()
