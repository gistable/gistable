# -*- coding: utf-8 -*-
'''
Created on 17.03.2012

@author: moschlar
'''

import tw2.core as twc
import tw2.forms as twf
import tw2.sqla as twsa
import tw2.bootstrap as twb

from awesome.model import Group, User


class DbSelectionField(twf.SelectionField):
    entity = twc.Param('SQLAlchemy mapped class to use', request_local=False)
    query = twc.Param()

    def prepare(self):
        self.options = [(x.id, unicode(x)) for x in self.query.all()]
        super(DbSelectionField, self).prepare()


class GroupSelectField(twb.SingleSelectField, DbSelectionField):
    @classmethod
    def post_define(cls):
        if getattr(cls, 'entity', None):
            cls.validator = twsa.RelatedValidator(entity=cls.entity)


class UserForm(twb.HorizontalForm):

    id = twf.HiddenField()

    group_id = GroupSelectField(
        entity=Group,
    )

    def prepare(self):
        self.child.c.group_id.query = \
            Group.query.filter(
                Group.id.in_(User.query.get(self.value.id).groups)
            )
        super(UserForm, self).prepare()
