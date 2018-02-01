from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField

import imghdr


class ImageFileRequired(object):
    """
    Validates that an uploaded file from a flask_wtf FileField is, in fact an
    image.  Better than checking the file extension, examines the header of
    the image using Python's built in imghdr module.
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data is None or imghdr.what('unused', field.data.read()) is None:
            message = self.message or 'An image file is required'
            raise validators.StopValidation(message)

        field.data.seek(0)


class MyForm(Form):
    
    photo = FileField('Photo', validators=[ImageFileRequired()])
