from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth


class UnsupportedFormat(requests.HTTPError):
    pass


class Client(object):
    def __init__(self):
        self.client_id = settings.NOTUBE_CLIENT_ID
        self.client_secret = settings.NOTUBE_CLIENT_SECRET
        self.domain = settings.NOTUBE_DOMAIN

    def _request(self, endpoint, method, **kwargs):
        req_kwargs = {
            'auth': HTTPBasicAuth(self.client_id, self.client_secret),
        }
        if method == 'get':
            req_kwargs['params'] = kwargs
        else:
            req_kwargs['data'] = kwargs

        r = requests.request(method, "http://%s/api/%s" % (self.domain, endpoint), **req_kwargs)
        r.raise_for_status()
        return r.json()

    def create_upload(self, filename):
        try:
            return self._request('upload', 'post', filename=filename)
        except requests.HTTPError, e:
            if e.response.status_code == 400:
                raise UnsupportedFormat(e)
            raise e

    def complete_upload(self, upload_id, notification_url):
        return self._request("upload/%s/complete" % upload_id, 'post', notification=notification_url)

    def upload(self, upload_id):
        return self._request("upload/%s" % upload_id, 'get')

    def embed_url(self, id):
        return "http://%s/media/%s" % (self.domain, id)

    def delete_task(self, task_id):
        return self._request("task/%s" % task_id, 'delete')

    def create_task(self, url, notification_url):
        return self._request('task', 'post', url=url, notification=notification_url)

    def resubmit_task(self, task_id, url=None, notification_url=None):
        return self._request("task/%s/resubmit" % task_id, 'post', url=url, notification=notification_url)

    def notify_task(self, task_id, notification_url=None):
        return self._request("task/%s/notify" % task_id, 'post', notification=notification_url)

    def task(self, task_id):
        return self._request("task/%s" % task_id, 'get')

    def task_list(self, **kwargs):
        return self._request("task", 'get', **kwargs)

