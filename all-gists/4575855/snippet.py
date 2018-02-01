from django.test import client

# Call this function on head of your test file.

def patch_request_factory():
    def _method(self, path, data='', content_type='application/octet-stream', follow=False, **extra):
        response = self.generic("PATCH", path, data, content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    if not hasattr(client, "_patched"):
        client._patched = True
        client.Client.patch = _method

