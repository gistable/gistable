import time
from django.utils.http import http_date

AJAX_NEGATIVE_CHECK_EXPIRES = 60 # object is still available
AJAX_POSITIVE_CHECK_EXPIRES = 60*10 # if object is not available (or taken)

def check_ajax(request):
    # do stuff here
    timeout = AJAX_NEGATIVE_CHECK_EXPIRES if avail else AJAX_POSITIVE_CHECK_EXPIRES

    response = HttpResponse(json_result, mimetype='application/json')
    response['Expires'] = http_date(time.time() + timeout)
    return response
