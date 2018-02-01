# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from settings.base import get_env_variable

from azure.storage import BlobService


@deconstructible
class AzureBlobStorage(Storage):

    def __init__(self, account='nyxstorage', container='pxo'):
        self.base_storage_uri = 'http://%s.blob.core.windows.net/%s/' % (
            account, container)
        self.blob_service = BlobService(
            account, get_env_variable('AZURE_BLOB_STORAGE_KEY'))
        self.container = container

    def _open(self, name, mode='rb'):
        data = self.blob_service.get_blob(self.container, name)
        return ContentFile(data)

    def _save(self, name, content):
        _file = content.read()
        file_name = content.name[-35:]
        self.blob_service.put_blob(
            self.container, file_name, _file, x_ms_blob_type='BlockBlob')
        return self.base_storage_uri + file_name

    def create_container(self, container_name):
        result = self.blob_service.create_container(
            container_name, x_ms_blob_public_access='container')
        return result

    def delete(self, name):
        self.blob_service.delete_blob(self.container, name)

    def exists(self, name):
        try:
            self.blob_service.get_blob_properties(self.container, name)
        except:
            return False
        else:
            return True

    def get_available_name(self, name):
        return name

    def get_blobs(self):
        blobs = self.blob_service.list_blobs(self.container)
        return blobs

    def get_valid_name(self, name):
        return name

    def modified_time(self, name):
        metadata = self.blob_service.get_blob_metadata(self.container, name)
        modified_time = float(metadata.get('x-ms-meta-modified_time'))
        return datetime.fromtimestamp(modified_time)

    def set_public_container(self, container_name):
        result = self.blob_service.set_container_acl(
            container_name, x_ms_blob_public_access='container')
        return result

    def size(self, name):
        properties = self.blob_service.get_blob_properties(
            self.container, name)
        return properties.get('content-length')

    def url(self, name):
        blob = self.blob_service.list_blobs(self.container, prefix=name)
        return blob.blobs[0].url