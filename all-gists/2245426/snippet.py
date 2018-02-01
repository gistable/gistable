# -*- coding: utf-8 -*-

from flask.ext.admin import datastore
from flask.ext.admin import util
from flask.ext.wtf import Form
from pymongo.objectid import ObjectId
from pymongo.errors import OperationFailure


class Any(object):
    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])


class DictForm(Form):
    def process(self, formdata=None, obj=None, **kwargs):
        obj = Any(**obj) if isinstance(obj, dict) else obj
        super(DictForm, self).process(formdata, obj, **kwargs)
        

    def populate_obj(self, obj):
        scapegoat = Any()
        super(Form, self).populate_obj(scapegoat)
        for attr in scapegoat.__dict__:
            obj[attr] = getattr(scapegoat, attr)


class PyMongoDatastore(datastore.AdminDatastore):
    def __init__(self, collections, mongo, document_forms, document_reprs={}):
        self.collections = collections
        self.mongo = mongo
        self.document_forms = document_forms
        self.document_reprs = document_reprs
        self._document_classes = {}

    def create_model_pagination(self, model_name, page, per_page=25):
        """Returns a pagination object for the list view."""
        return PyMongoPagination(page, per_page, self.get_model_collection(model_name), self.get_model_class(model_name))

    def delete_model_instance(self, model_name, model_keys):
        """Deletes a model instance. Returns True if model instance
        was successfully deleted, returns False otherwise.
        """
        try:
            self.get_model_collection(model_name).remove(ObjectId(model_keys[0]))
            return True
        except OperationFailure:
            return False

    def find_model_instance(self, model_name, model_keys):
        """Returns a model instance, if one exists, that matches
        model_name and model_keys. Returns None if no such model
        instance exists.
        """
        return self.get_model_collection(model_name).find_one(ObjectId(model_keys[0]), as_class=self.get_model_class(model_name))

    def get_model_class(self, model_name):
        """Returns a model class, given a model name."""
        if model_name not in self._document_classes:
            class DocumentClass(self.mongo.cx.document_class):
                collection_name = model_name
            if model_name in self.document_reprs:
                DocumentClass.__repr__ = self.document_reprs[model_name]

            self._document_classes[model_name] = DocumentClass

            del DocumentClass
        return self._document_classes[model_name] 

    def get_model_collection(self, model_name):
        """Returns a model collection, given a model name."""
        return self.mongo.db[model_name]

    def get_model_form(self, model_name):
        """Returns a form, given a model name."""
        try:
            return self.document_forms[model_name]
        except KeyError:
            raise Exception('You must specify the form to use for a model via document_forms')

    def get_model_keys(self, model_instance):
        """Returns the keys for a given a model instance. This should
        be an iterable (e.g. list or tuple) containing the keys.
        """
        return [model_instance['_id']]

    def list_model_names(self):
        """Returns a list of model names available in the datastore."""
        return self.collections

    def save_model(self, model_instance):
        """Persists a model instance to the datastore. Note: this
        could be called when a model instance is added or edited.
        """
        self.mongo.db[model_instance.collection_name].save(model_instance)

    def update_from_form(self, model_instance, form):
        """Returns a model instance whose values have been updated
        with the values from a given form.
        """
        saved_id = None
        if '_id' in model_instance:
            saved_id = model_instance['_id']
        form.populate_obj(model_instance)
        if saved_id:
            model_instance['_id'] = saved_id
        return model_instance


class PyMongoPagination(util.Pagination):
    def __init__(self, page, per_page, collection, as_class, *args, **kwargs):
        total = collection.count()
        items = collection.find(skip=(page - 1) * per_page, limit=per_page, as_class=as_class)
        super(PyMongoPagination, self).__init__(
            page, per_page, total=total, items=items,
            *args, **kwargs)
