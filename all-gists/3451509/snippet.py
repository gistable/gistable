import datetime
import httplib2
# to see in detail what's going on, uncomment
# httplib2.debuglevel = 4

from apiclient.discovery import build
from oauth2client.client import OAuth2Credentials, OAuth2WebServerFlow


if __name__ == "__main__":

    flow = OAuth2WebServerFlow(client_id="client_id_from_Console.apps.googleusercontent.com",
                               client_secret="client_secret_from_Console",
                               scope="https://www.googleapis.com/auth/androidpublisher")
    auth_url = flow.step1_get_authorize_url(redirect_uri="http://localhost")

    # the auth_url looks similar to this:
    # https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fandroidpublisher&redirect_uri=http%3A%2F%2Flocalhost%2Foauth2callback&response_type=code&client_id=client_id_from_Console.apps.googleusercontent.com&access_type=offline
    # open it up in the browser, log in with the appropriate Google account and press the Allow button
    # after redirect, extract the code parameter from the URL
    code = "4/kGRRVluW_MustsRmVcL2azzPHVFu.UuoPHSEws3AXOl01ti4ZT3YBGCqocgI"
    flow_credentials = flow.step2_exchange(code)

    # the flow_credentials object contains the refresh_token property,
    # the one we're interested in; store it for later use
    
    credentials = OAuth2Credentials("FUBAR", # random value for access token, does not matter
                                    "client_id_from_Console.apps.googleusercontent.com",
                                    "client_secret_from_Console",
                                    flow_credentials.refresh_token,
                                    datetime.datetime.now(),
                                    "https://accounts.google.com/o/oauth2/token",
                                    "wildfuse/1.0") # be a good citizen and pass a custom User-Agent too

    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build("androidpublisher", "v1", http=http)

    # get the packageName, productId and purchaseToken from the Android client
    validation_request = service.purchases().get(packageName=packageName,
                                                 subscriptionId=productId,
                                                 token=purchaseToken)

    # example return value of the validation_request.execute() call
    #
    # {u'initiationTimestampMsec': u'1340280336000',
    #  u'kind': u'androidpublisher#subscriptionPurchase',
    #  u'autoRenewing': False,
    #  u'validUntilTimestampMsec': u'1342879522220'}
    print validation_request.execute()

