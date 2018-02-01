import threading

from oauth2client.client import Storage as BaseStorage
from oauth2client.client import Credentials
from oauth2client.anyjson import simplejson

def from_dict(container):
    """
    Create a Credentials object from a dictionary.

    The dictionary is first converted to JSON by the native implementation
    to ensure it is converted correctly and make updates to the oauth2client module
    easier.
    """
    jsonRepr = simplejson.dumps(container)
    return Credentials.new_from_json(jsonRepr)

def to_dict(credentials):
    """
    Convert a Credentials object to a dictionary.

    The Credentials object is first converted to JSON by the native implementation
    to ensure it is converted correctly and make updates to the oauth2client module
    easier.
    """
    jsonRepr = credentials.to_json()
    dictRepr = simplejson.loads(jsonRepr)

    return dictRepr

class DictStorage(BaseStorage):
    """
    Storage implementation for storing credentials inside an existing dictionary object.
    """

    def __init__(self, container, key='credentials'):
        if not isinstance(container, dict):
            raise Exception('Container must be an instance of a dict')

        self._container = container
        self._key = key
        self._lock = threading.Lock()

    def locked_get(self):
        """Retrieve Credential from Config.

        Returns:
          oauth2client.client.Credentials
        """
        credentials = None
        try:
            credentials = from_dict(self._container[self._key])
        except KeyError:
            pass

        return credentials

    def locked_put(self, credentials):
        """Write Credentials to the Config.

        Args:
          credentials: Credentials, the credentials to store.
        """
        d = to_dict(credentials)
        self._container[self._key] = d

    def locked_delete(self):
        """Delete Credentials from Config.
        """
        del self._container[self._key]