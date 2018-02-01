import json
import requests
from django.views.decorators.csrf import csrf_exempt

FB_MESSENGER_ACCESS_TOKEN = "[TOKEN]"


def respond_FB(sender_id, text):
    json_data = {
        "recipient": {"id": sender_id},
        "message": {"text": text + " to you!"}
    }
    params = {
        "access_token": FB_MESSENGER_ACCESS_TOKEN
    }
    r = requests.post('https://graph.facebook.com/v2.6/me/messages', json=json_data, params=params)
    print(r, r.status_code, r.text)


@csrf_exempt
def fb_webhook(request):
    if request.method == "GET":
        if (request.GET.get('hub.verify_token') == 'this_is_a_verify_token_created_by_sean'):
            return HttpResponse(request.GET.get('hub.challenge'))
        return HttpResponse('Error, wrong validation token')

    if request.method == "POST":
        body = request.body
        print("BODY", body)
        messaging_events = json.loads(body.decode("utf-8"))
        print("JSON BODY", body)
        sender_id = messaging_events["entry"][0]["messaging"][0]["sender"]["id"]
        message = messaging_events["entry"][0]["messaging"][0]["message"]["text"]
        respond_FB(sender_id, message)
        return HttpResponse('Received.')