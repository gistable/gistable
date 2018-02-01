# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        db.execute('UPDATE auth_user SET password=CONCAT("bcrypt", SUBSTR(password, 3)) WHERE password LIKE "bc$%%"')

    def backwards(self, orm):
        db.execute('UPDATE auth_user SET password=CONCAT("bc", SUBSTR(password, 7)) WHERE password LIKE "bcrypt$%%"')