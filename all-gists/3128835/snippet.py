from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.files.base import File
from dropbox.client import DropboxClient
from dropbox.session import DropboxSession
from django.conf import settings
import os

class DropboxFileUploadHandler(TemporaryFileUploadHandler):
    def __init__(self, *args, **kwargs):
        super(DropboxFileUploadHandler, self).__init__(*args, **kwargs)
        fallback_dropbox_folder = getattr(settings, "DROPBOX_FILE_UPLOAD_FOLDER", "/")
        self.dropbox_folder = kwargs.get("dropbox_folder", fallback_dropbox_folder)
        access_type = getattr(settings, "DROPBOX_ACCESS_TYPE", "app_folder")
        dropbox_session = DropboxSession(settings.DROPBOX_APP_KEY,
                                         settings.DROPBOX_APP_SECRET_KEY,
                                         access_type)
        dropbox_session.set_token(settings.DROPBOX_APP_ACCESS_TOKEN,
                                  settings.DROPBOX_APP_ACCESS_TOKEN_SECRET)
        self.dropbox_client = DropboxClient(dropbox_session)

    def file_complete(self, file_size):
        self.file = super(DropboxFileUploadHandler, self).file_complete(file_size)
        file_path = os.path.join(self.dropbox_folder, self.file.name)
        metadata = self.dropbox_client.put_file(file_path, self.file)
        return DropboxFile(metadata)


class DropboxFile(File):
    def __init__(self, file, name=None):
        self.dropbox_metadata = file
        name = name or os.path.basename(self.dropbox_metadata["path"])
        super(DropboxFile, self).__init__(file, name=name)
        self._size = self.dropbox_metadata["size"]
        access_type = getattr(settings, "DROPBOX_ACCESS_TYPE", "app_folder")
        dropbox_session = DropboxSession(settings.DROPBOX_APP_KEY,
                                         settings.DROPBOX_APP_SECRET_KEY,
                                         access_type)
        dropbox_session.set_token(settings.DROPBOX_APP_ACCESS_TOKEN,
                                  settings.DROPBOX_APP_ACCESS_TOKEN_SECRET)
        self.dropbox_client = DropboxClient(dropbox_session)

    def open(self, mode=None):
        self.file = self.dropbox_client.get_file(self.dropbox_metadata["path"])

    def close(self):
        pass