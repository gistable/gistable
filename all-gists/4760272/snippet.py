"""A notebook manager that uses S3 storage. (based on the Azure manager)
http://ipython.org/ipython-doc/dev/interactive/htmlnotebook.html#using-a-different-notebook-store

Drop this file in IPython/frontend/html/notebook

1. Create a new notebook profile - ipython profile create nbserver
2. edit ~/.ipython/profile_nbserver/ipython_notebook_config.py
3. Add these lines:

    c.NotebookApp.notebook_manager_class = 'IPython.frontend.html.notebook.s3nbmanager.S3NotebookManager'
    c.S3NotebookManager.aws_access_key_id     = u""
    c.S3NotebookManager.aws_secret_access_key = u""
    c.S3NotebookManager.bucket = u'<unique bucket name>'

4. Start with `ipython notebook --profile=nbserver`

Authors:
* Bradley Kreider
* Brian Granger
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2012  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import datetime

import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection

from tornado import web

from .nbmanager import NotebookManager
from IPython.nbformat import current
from IPython.utils.traitlets import Unicode, Instance


#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

class S3NotebookManager(NotebookManager):

    aws_access_key_id = Unicode('', config=True, help='AWS access key.')
    aws_secret_access_key = Unicode('', config=True, help='AWS S3 storage account key.')
    bucket = Unicode('', config=True, help='Bucket name for notebooks.')
    
    meta_nbname = "nbname"

    def __init__(self, **kwargs):
        super(S3NotebookManager, self).__init__(**kwargs)
        self.__s3_conn = None
        self.log_info()
        
        # Form unique bucket using access key + bucket name
        # Wanted to add access_key to this but lower() isn't working
        self.__bucket_name = self.bucket  
        self.__create_container()
        
    @property
    def s3_conn(self):
        """Lazy initialize"""
        if not self.__s3_conn:
            self.__s3_conn  = S3Connection(aws_access_key_id = self.aws_access_key_id,
                                           aws_secret_access_key = self.aws_secret_access_key)
        return self.__s3_conn

    def __create_container(self):
        if not self.s3_conn.lookup(self.__bucket_name):
            self.s3_conn.create_bucket(self.__bucket_name)

    def load_notebook_names(self):
        """On startup load the notebook ids and names from S3
        """
        self.mapping = {}
        bucket = self.s3_conn.get_bucket(self.__bucket_name)
        
        for item in bucket:
            id_ = item.name
            
            # bug in boto doesn't load metadata
            # Force metadata load with get_key
            item = bucket.get_key(id_)
            name =  item.get_metadata(self.meta_nbname)
            
            if name:
                self.mapping[id_] = name
            else:
                self.log.info(name)
                self.log.info(item.metadata)
                self.log.info("Skipping over S3 file with no ipython name: %s" % (id_,))
            
    def list_notebooks(self):
        """List all notebooks in the container.

        This version uses `self.mapping` as the authoritative notebook list.
        """
        try:
            data = [dict(notebook_id=item[0],name=item[1]) for item in self.mapping.items()]
            data = sorted(data, key=lambda item: item['name'])
        except Exception as e:
            self.log.info("Problem sorting, this is the mapping: %s" % (self.mapping.items()))
            raise
        
        return data

    def read_notebook_object(self, notebook_id):
        """Get the object representation of a notebook by notebook_id."""
        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)
        try:
            # v1 and v2 and json in the .ipynb files.
            bucket = self.s3_conn.get_bucket(self.__bucket_name)
            k = Key(bucket)
            k.key = notebook_id
            data = k.get_contents_as_string()
            #self.log.info("downloaded contents: %s" % (data,))
        except:
            raise web.HTTPError(500, u'Couldn\'t pull out of s3.')
            
        try:
            nb = current.reads(data, u'json')
        except:
            raise web.HTTPError(500, u'Unreadable JSON notebook.')
        # Todo: The last modified should actually be saved in the notebook document.
        # We are just using the current datetime until that is implemented.
        last_modified = datetime.datetime.utcnow()
        return last_modified, nb

    def write_notebook_object(self, nb, notebook_id=None):
        """Save an existing notebook object by notebook_id."""
        try:
            new_name = nb.metadata.name
        except AttributeError:
            raise web.HTTPError(400, u'Missing notebook name')

        if notebook_id is None:
            notebook_id = self.new_notebook_id(new_name)

        if notebook_id not in self.mapping:
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)

        try:
            data = current.writes(nb, u'json')
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while saving notebook: %s' % e)

        try:
            bucket = self.s3_conn.get_bucket(self.__bucket_name)
            key = Key(bucket)
            key.key = notebook_id
            key.set_metadata(self.meta_nbname, new_name)
            #self.log.info("Setting contents to: %s" % (data,))
            key.set_contents_from_string(data)
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while saving notebook: %s' % e)

        self.mapping[notebook_id] = new_name
        return notebook_id

    def delete_notebook(self, notebook_id):
        """Delete notebook by notebook_id."""
        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)
        try:
            bucket = self.s3_conn.get_bucket(self.__bucket_name)
            k = Key(bucket)
            k.key = notebook_id
            k.delete()
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while deleting notebook: %s' % e)
        else:
            self.delete_notebook_id(notebook_id)

    def log_info(self):
        self.log.info("Serving notebooks from S3 storage: %s, %s", self.aws_access_key_id, self.bucket)
