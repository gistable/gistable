## widget

import httplib2
from urllib import urlencode

import colander
from colander import null
from colander import Invalid

from deform.widget import CheckedInputWidget

from pyramid.settings import get_settings


@colander.deferred
def deferred_recaptcha_widget(node, kw):
    request = kw['request']
    class RecaptchaWidget(CheckedInputWidget):
        template = 'recaptcha_widget'
        readonly_template = 'recaptcha_widget'
        requirements = ()
        url = "http://www.google.com/recaptcha/api/verify"
        headers={'Content-type': 'application/x-www-form-urlencoded'}

        def serialize(self, field, cstruct, readonly=False):
            if cstruct in (null, None):
                cstruct = ''
            confirm = getattr(field, 'confirm', '')
            template = readonly and self.readonly_template or self.template
            return field.renderer(template, field=field, cstruct=cstruct,
                                  public_key=get_settings()['public_key'],
                                  )

        def deserialize(self, field, pstruct):
            if pstruct is null:
                return null
            challenge = pstruct.get('recaptcha_challenge_field') or ''
            response = pstruct.get('recaptcha_response_field') or ''
            if not response:
                raise Invalid(field.schema, 'No input')
            if not challenge:
                raise Invalid(field.schema, 'Missing challenge')
            privatekey = get_settings()['private_key']
            remoteip = self.request.remote_addr
            data = urlencode(dict(privatekey=privatekey,
                                  remoteip=remoteip,
                                  challenge=challenge,
                                  response=response))
            h = httplib2.Http(timeout=10)
            try:
                resp, content = h.request(self.url,
                                          "POST",
                                          headers=self.headers,
                                          body=data)
            except AttributeError as e:
                if e=="'NoneType' object has no attribute 'makefile'":
                    ## XXX: catch a possible httplib regression in 2.7 where
                    ## XXX: there is no connextion made to the socker so
                    ## XXX sock is still None when makefile is called.
                    raise Invalid(field.schema,
                                  "Could not connect to the captcha service.")
            if not resp['status'] == '200':
                raise Invalid(field.schema,
                              "There was an error talking to the recaptcha \
                              server{0}".format(resp['status']))
            valid, reason = content.split('\n')
            if not valid == 'true':
                if reason == 'incorrect-captcha-sol':
                    reason = "Incorrect solution"
                raise Invalid(field.schema, reason.replace('\\n', ' ').strip("'") )
            return pstruct

    return RecaptchaWidget(request=request)



## Schema
class SimpleUserSchema(colander.MappingSchema):
    __uid__=colander.SchemaNode(colander.String(),
                                title="Username",
                                description="The name of the participant",
                                validator=deferred_username_validator)
    display_name=colander.SchemaNode(colander.String(),
                                     missing=colander.null,
                                     title="Display Name",
                                     widget=\
                                     deform.widget.TextInputWidget(size=40))
    email=colander.SchemaNode(colander.String(),
                              title="email",
                              description=\
                              'Type your email address and confirm it',
                              validator=colander.Email(),
                              widget=email_widget)
    password=colander.SchemaNode(colander.String(),
                                 validator=colander.Length(min=6),
                                 widget = \
                                 deform.widget.CheckedPasswordWidget(size=40),
                                 description= \
                                 "Type your password and confirm it")
    captcha=colander.SchemaNode(colander.String(),
                                title='Verify you are human',
                                widget=deferred_recaptcha_widget)


## widget template

<input type="hidden" name="__start__" value="${field.name}:mapping"/>
    <script type="text/javascript"
       src="http://www.google.com/recaptcha/api/challenge?k=${public_key}">
    </script>
    <noscript>
      <iframe src="http://www.google.com/recaptcha/api/noscript?k=${public_key}"
	      height="300" width="500" frameborder="0"></iframe><br />
      <input type="text"
	     name="recaptcha_challenge_field"
	     id="${field.oid}"/>

      <input type="hidden"
	     name="recaptcha_response_field"
	     id="${field.oid}-recaptcha_response_field"/>
    </noscript>
<input type="hidden" name="__end__" value="${field.name}:mapping"/>
